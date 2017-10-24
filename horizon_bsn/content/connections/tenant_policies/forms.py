# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django.core.urlresolvers import reverse
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages

from horizon_bsn.api import neutron

import logging

LOG = logging.getLogger(__name__)


class RuleCIDRField(forms.IPField):
    """Extends IPField to allow ('any','external') keywords and requires CIDR

    """
    def __init__(self, *args, **kwargs):
        kwargs['mask'] = True
        super(RuleCIDRField, self).__init__(*args, **kwargs)

    def validate(self, value):
        keywords = ['any', 'external']
        if value in keywords:
            self.ip = value
        else:
            if '/' not in value:
                raise ValidationError(_("Input must be in CIDR format"))
            super(RuleCIDRField, self).validate(value)


class PortField(forms.DecimalField):
    """Port number input

    """
    def validate(self, value):
        if int(value) not in range(0, 65536):
            raise ValidationError(_("Port must be in the range of 0 to 65535"))
        super(PortField, self).validate(value)


class AddTenantPolicy(forms.SelfHandlingForm):
    priority = forms.ChoiceField(label=_("Priority"),
                                 help_text=_("Select a Priority for the "
                                             "policy. Lower value = higher "
                                             "priority."))
    source = RuleCIDRField(label=_("Source CIDR"), widget=forms.TextInput())
    source_port = PortField(required=False, initial=0)
    destination = RuleCIDRField(label=_("Destination CIDR"),
                                widget=forms.TextInput())
    destination_port = PortField(required=False, initial=0)
    action = forms.ChoiceField(label=_("Action"))
    protocol = forms.ChoiceField(label=_("Protocol"),
                                 help_text=_("Protocol is mandatory when "
                                             "specifying port for the policy "
                                             "traffic."), required=False)
    nexthops = forms.MultiIPField(label=_("Optional: Next Hop "
                                          "Addresses (comma delimited)"),
                                  help_text=_("Next Hop field is ignored for "
                                              "Deny action"),
                                  widget=forms.TextInput(), required=False)
    failure_url = 'horizon:project:connections:index'

    def __init__(self, request, *args, **kwargs):
        super(AddTenantPolicy, self).__init__(request, *args, **kwargs)
        self.fields['action'].choices = [('permit', _('Permit')),
                                         ('deny', _('Deny'))]
        self.fields['priority'].choices = self.populate_priority_choices(
            request)
        self.fields['protocol'].choices = [('', _('None')),
                                           ('tcp', 'TCP'),
                                           ('udp', 'UDP')]

    def populate_priority_choices(self, request):
        existing_priorities = []
        all_policies = neutron.tenantpolicy_list(
            request, **{'tenant_id': request.user.project_id})
        for policy in all_policies:
            existing_priorities.append(policy['priority'])

        priorities = [(prio, prio) for prio in range(3000, 0, -1)
                      if prio not in existing_priorities]
        if priorities:
            priorities.insert(0, ("", _("Select a Priority")))
        else:
            priorities.insert(0, ("", _("No Priorities available")))
        return priorities

    def clean(self):
        cleaned_data = super(AddTenantPolicy, self).clean()
        if 'priority' not in cleaned_data:
            cleaned_data['priority'] = -1
        if 'nexthops' not in cleaned_data:
            cleaned_data['nexthops'] = ''
        if 'source' in cleaned_data and cleaned_data['source'] == '0.0.0.0/0':
            cleaned_data['source'] = 'any'
        if ('destination' in cleaned_data
                and cleaned_data['destination'] == '0.0.0.0/0'):
            cleaned_data['destination'] = 'any'
        if 'action' in cleaned_data and cleaned_data['action'] == 'deny':
            cleaned_data['nexthops'] = ''
        return cleaned_data

    def _validate_protocol(self, data):
        if ((int(data['source_port']) > 0 or int(data['destination_port']) > 0)
                and data['protocol'] not in ['tcp', 'udp']):
            raise ValidationError('Protocol must be specified if either '
                                  'source or destination port is specified')

    def handle(self, request, data, **kwargs):
        try:
            self._validate_protocol(data)
            tenantpolicy = neutron.tenantpolicy_create(request, **data)
            msg = _("Tenant Policy was successfully created")
            LOG.debug(msg)
            messages.success(request, msg)
            return tenantpolicy
        except Exception as e:
            msg = _('Failed to add router rule %s') % e
            LOG.info(msg)
            messages.error(request, msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
