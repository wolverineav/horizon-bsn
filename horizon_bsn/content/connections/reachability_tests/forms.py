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

from django.forms import ValidationError  # noqa
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon.forms import fields
from horizon import messages

from horizon_bsn.api import neutron
import logging
from openstack_dashboard.api import neutron as osneutron

import re

LOG = logging.getLogger(__name__)

NEW_LINES = re.compile(r"\r|\n")
EXPECTATION_CHOICES = [('default', _('--- Select Result ---')),
                       ('dropped by route', _('dropped by route')),
                       ('dropped by policy', _('dropped by policy')),
                       ('not permitted by security groups',
                        _('not permitted by security groups')),
                       ('dropped due to private segment',
                        _('dropped due to private segment')),
                       ('dropped due to loop', _('dropped due to loop')),
                       ('packet in', _('packet in')),
                       ('forwarded', _('forwarded')),
                       ('dropped', _('dropped')),
                       ('unspecified source', _('unspecified source')),
                       ('unsupported', _('unsupported')),
                       ('invalid input', _('invalid input')),
                       ('inconsistent status', _('inconsistent status')),
                       ('no traffic detected', _('no traffic detected'))]


class CreateReachabilityTest(forms.SelfHandlingForm):

    name = forms.CharField(max_length="64",
                           label=_("Name"),
                           required=True)

    src_tenant_name = forms.ChoiceField(
        label=_("Source Tenant"),
        help_text=_("Test reachability for current tenant only."))

    src_segment_name = forms.ChoiceField(
        label=_("Source Segment"),
        help_text=_("Select a source segment name."))

    def __init__(self, request, *args, **kwargs):
        super(CreateReachabilityTest, self).__init__(request, *args, **kwargs)
        self.fields['src_tenant_name'].choices = self\
            .populate_tenant_choices(request)
        self.fields['src_tenant_name'].widget.attrs['readonly'] = True
        self.fields['src_segment_name'].choices = self\
            .populate_segment_choices(request)

    def populate_tenant_choices(self, request):
        return [(request.user.tenant_name, request.user.tenant_name)]

    def populate_segment_choices(self, request):
        networks = osneutron.network_list(request,
                                          tenant_id=request.user.project_id,
                                          shared=False)
        segment_list = [(network.name, network.name) for network in networks]
        if segment_list:
            segment_list.insert(0, ("", _("Select a Segment")))
        else:
            segment_list.insert(0, ("", _("No segments available")))
        return segment_list

    src_ip = fields.IPField(
        label=_("Source IP Address"),
        required=True,
        initial="0.0.0.0")

    dst_ip = fields.IPField(
        label=_("Destination IP Address"),
        required=True,
        initial="0.0.0.0")

    expected_result = forms.ChoiceField(
        label=_('Expected Connection Results'),
        required=True,
        choices=EXPECTATION_CHOICES,
        widget=forms.Select(
            attrs={'class': 'switchable',
                   'data-slug': 'expected_result'}))

    def clean(self):
        cleaned_data = super(CreateReachabilityTest, self).clean()

        def update_cleaned_data(key, value):
            cleaned_data[key] = value
            self.errors.pop(key, None)

        expected_result = cleaned_data.get('expected_result')

        if expected_result == 'default':
            msg = _('A expected connection result must be selected.')
            raise ValidationError(msg)

        return cleaned_data

    def handle(self, request, data):
        try:
            reachabilitytest = neutron.reachabilitytest_create(request, **data)
            msg = _("Reachability Test %s was successfully created") \
                % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return reachabilitytest
        except Exception:
            exceptions.handle(request,
                              _("Failed to create reachability test"))


class UpdateForm(CreateReachabilityTest):
    id = forms.CharField(max_length="36", widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(UpdateForm, self).clean()

        def update_cleaned_data(key, value):
            cleaned_data[key] = value
            self.errors.pop(key, None)

        expected_result = cleaned_data.get('expected_result')
        if expected_result == 'default':
            msg = _('A expected connection result must be selected.')
            raise ValidationError(msg)

        return cleaned_data

    def handle(self, request, data):
        try:
            id = data['id']
            reachabilitytest = neutron \
                .reachabilitytest_update(request, id, **data)
            msg = _("Reachability Test %s was successfully updated") \
                % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return reachabilitytest
        except Exception:
            exceptions.handle(request,
                              _("Failed to update reachability test"))


class RunQuickTestForm(forms.SelfHandlingForm):

    src_tenant_name = forms.ChoiceField(
        label=_("Source Tenant"),
        help_text=_("Select a source tenant name."))

    src_segment_name = forms.ChoiceField(
        label=_("Source Segment"),
        help_text=_("Select a source segment name."))

    def __init__(self, request, *args, **kwargs):
        super(RunQuickTestForm, self).__init__(request, *args, **kwargs)
        self.fields['src_tenant_name'].choices = self\
            .populate_tenant_choices(request)
        self.fields['src_segment_name'].choices = self\
            .populate_segment_choices(request)

    def populate_tenant_choices(self, request):
        return [(request.user.tenant_name, request.user.tenant_name)]

    def populate_segment_choices(self, request):
        networks = osneutron.network_list(request,
                                          tenant_id=request.user.project_id,
                                          shared=False)
        segment_list = [(network.name, network.name) for network in networks]
        if segment_list:
            segment_list.insert(0, ("", _("Select a Segment")))
        else:
            segment_list.insert(0, ("", _("No segments available")))
        return segment_list

    src_ip = fields.IPField(
        label=_("Source IP Address"),
        required=True,
        initial="0.0.0.0")

    dst_ip = fields.IPField(
        label=_("Destination IP Address"),
        required=True,
        initial="0.0.0.0")

    expected_result = forms.ChoiceField(
        label=_('Expected Connection Results'),
        required=True,
        choices=EXPECTATION_CHOICES,
        widget=forms.Select(
            attrs={'class': 'switchable',
                   'data-slug': 'expected_connection'}))

    def clean(self):
        cleaned_data = super(RunQuickTestForm, self).clean()

        def update_cleaned_data(key, value):
            cleaned_data[key] = value
            self.errors.pop(key, None)

        expected_result = cleaned_data.get('expected_result')
        if expected_result == 'default':
            msg = _('A expected connection result must be selected.')
            raise ValidationError(msg)

        return cleaned_data

    def handle(self, request, data):
        data['name'] = "quicktest_" + str(request.user.project_id)
        try:
            reachabilityquicktest = neutron \
                .reachabilityquicktest_get(request, request.user.project_id)
            # update with new fields
            neutron.reachabilityquicktest_update(
                request, request.user.project_id, **data)
        except Exception:
            # test doesn't exist, create
            reachabilityquicktest = neutron.reachabilityquicktest_create(
                request, **data)
        # clear dict
        data = {}
        # set run_test to true and update test to get results
        data['run_test'] = True
        reachabilityquicktest = neutron.reachabilityquicktest_update(
            request, reachabilityquicktest.id, **data)
        return reachabilityquicktest


class SaveQuickTestForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255",
                           label=_("Name"),
                           required=True)

    def clean(self):
        cleaned_data = super(SaveQuickTestForm, self).clean()

        def update_cleaned_data(key, value):
            cleaned_data[key] = value
            self.errors.pop(key, None)

        return cleaned_data

    def handle(self, request, data):
        try:
            data['save_test'] = True
            reachabilityquicktest = neutron.reachabilityquicktest_update(
                request, request.user.project_id, **data)
            messages.success(
                request, _('Successfully saved quicktest %s') % data['name'])
            return reachabilityquicktest
        except Exception:
            messages.error(
                request, _('Failed to save quicktest %s') % data['name'])
