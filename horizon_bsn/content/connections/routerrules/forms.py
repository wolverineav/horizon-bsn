# Copyright 2013,  Big Switch Networks
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

import logging

from django.core.exceptions import ValidationError  # noqa
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon_bsn.content.connections.routerrules import rulemanager

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


class AddRouterRule(forms.SelfHandlingForm):
    router = forms.ChoiceField(label=_("Router"),
                               help_text=_("Select a Router."))

    priority = forms.ChoiceField(label=_("Priority"),
                                 help_text=_("Select a Priority for the "
                                             "policy. Lower value = higher "
                                             "priority."))
    source = RuleCIDRField(label=_("Source CIDR"),
                           widget=forms.TextInput())
    destination = RuleCIDRField(label=_("Destination CIDR"),
                                widget=forms.TextInput())
    action = forms.ChoiceField(label=_("Action"))
    nexthops = forms.MultiIPField(label=_("Optional: Next Hop "
                                          "Addresses (comma delimited)"),
                                  help_text=_("Next Hop field is ignored for "
                                              "Deny action"),
                                  widget=forms.TextInput(), required=False)
    failure_url = 'horizon:project:connections:index'

    def __init__(self, request, *args, **kwargs):
        super(AddRouterRule, self).__init__(request, *args, **kwargs)
        self.fields['action'].choices = [('permit', _('Permit')),
                                         ('deny', _('Deny'))]
        self.fields['router'].choices = self.populate_router_choices(
            request, self.request.META['routers_dict'])
        self.fields['priority'].choices = self.populate_priority_choices(
            request, self.request.META['routers_dict'])

    def populate_router_choices(self, request, routers_dict):
        routers = [(router.id, router.name)
                   for router in routers_dict.values()]
        if routers:
            routers.insert(0, ("", _("Select a Router")))
        else:
            routers.insert(0, ("", _("No Routers available")))
        return routers

    def populate_priority_choices(self, request, routers_dict):
        existing_priorities = []
        for router in routers_dict.values():
            for rule in router.router_rules:
                existing_priorities.append(rule['priority'])

        priorities = [(prio, prio) for prio in range(3000, 0, -1)
                      if prio not in existing_priorities]
        if priorities:
            priorities.insert(0, ("", _("Select a Priority")))
        else:
            priorities.insert(0, ("", _("No Priorities available")))
        return priorities

    def clean(self):
        cleaned_data = super(AddRouterRule, self).clean()
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

    def handle(self, request, data, **kwargs):
        try:
            rule = {'priority': data['priority'],
                    'action': data['action'],
                    'source': data['source'],
                    'destination': data['destination'],
                    'nexthops': data['nexthops'].split(',')}
            rulemanager.add_rule(request, router_id=data['router'],
                                 newrule=rule)
            msg = _('Router policy action performed successfully.')
            LOG.debug(msg)
            messages.success(request, msg)
            return True
        except Exception as e:
            msg = _('Failed to add router rule %s') % e
            LOG.info(msg)
            messages.error(request, msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
