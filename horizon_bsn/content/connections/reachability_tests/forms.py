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

import ast
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


def extract_src_tenant_and_segment(obj):
    """Extract src_tenant and src_segment from obj

    :param obj: an object that contains src_tenant and src_segment string
            eg. obj['src_tenant']\
                =u"{'tenant_id': u'tenant_id',
                    'tenant_name':  u'tenant_name'}"
                obj['src_segment']\
                =u"{'segment_id': u'segment_id',
                    'segment_name':  u'segment_name'}"
    :return: this operates on the original object
             tenant and segment info will be extracted from the obj
             src_tenant and src_segment are deleted after the operation
              eg.
                obj{ ...#other attr
                     'src_tenant_id'=u'tenant_id',
                     'src_tenant_name'=u'tenant_name',
                     'src_segment_id'=u'segment_id',
                     'src_segment_name'=u'segment_name'
                    }
    """
    if obj.get('src_tenant'):
        src_tenant = ast.literal_eval(obj['src_tenant'])

        obj['src_tenant_id'] = src_tenant.get('tenant_id')
        obj['src_tenant_name'] = src_tenant.get('tenant_name')

        del(obj['src_tenant'])

    if obj.get('src_segment'):
        src_segment = ast.literal_eval(obj['src_segment'])

        obj['src_segment_id'] = src_segment.get('segment_id')
        obj['src_segment_name'] = src_segment.get('segment_name')

        del(obj['src_segment'])


def populate_tenant_choices(request):
    """Returns a list of tenant info tuple for creating select options

    This only creates 1 option, which is user's current tenant/project
    :param request: object that contents tenant info
             -  request.user.tenant_name
             -  request.user.tenant_id
    :return: [(tenant_obj, tenant_display_string)]
            eg.
              [{'tenant_id':u'tenant_id', 'tenant_name': u'tenant_name'},
              u'tenant_name (tenant_id)']
    """
    # tenant_name (tenant_id)
    display = '%s (%s)' % (request.user.tenant_name,
                           request.user.tenant_id)
    value = {'tenant_name': request.user.tenant_name,
             'tenant_id': request.user.tenant_id}
    return [(value, display)]


def populate_segment_choices(request):
    """Returns a list of segment info tuples for creating select options

    This creates the list based on current project
    :param request: request info
             -  request.user.project_id
    :return: [(segment_obj, segment_display_string)]
            eg1. Has a segment name
              [{'segment_id':u'tenant_id', 'segment_name': u'segment_name'},
              u'segment_name (segment_id)']
            eg2. No segment name
              [{'segment_id':u'tenant_id', 'segment_name': u'segment_name'},
              u'segment_name (segment_id)']
    """
    networks = osneutron.network_list(request,
                                      tenant_id=request.user.project_id,
                                      shared=False)
    segment_list = []
    for network in networks:
        value = {'segment_id': network.id,
                 'segment_name': network.name}
        if network.name:
            # segment_name (segment_id)
            display = '%s (%s)' % (network.name, network.id)
        else:
            # (segment_id)
            display = '(%s)' % network.id
        segment_list.append((value, display))

    if segment_list:
        segment_list.insert(0, ("", _("Select a Segment")))
    else:
        segment_list.insert(0, ("", _("No segments available")))
    return segment_list


class CreateReachabilityTest(forms.SelfHandlingForm):

    name = forms.CharField(max_length="64",
                           label=_("Name"),
                           required=True)

    src_tenant = forms.ChoiceField(
        label=_("Source Tenant"),
        help_text=_("Test reachability for current tenant only."))

    src_segment = forms.ChoiceField(
        label=_("Source Segment"),
        help_text=_("Select a source segment."))

    def __init__(self, request, *args, **kwargs):
        super(CreateReachabilityTest, self).__init__(request, *args, **kwargs)

        self.fields['src_tenant'].choices = populate_tenant_choices(request)
        self.fields['src_tenant'].widget.attrs['readonly'] = True
        self.fields['src_segment'].choices = populate_segment_choices(request)

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
            extract_src_tenant_and_segment(data)
            reachabilitytest = neutron.reachabilitytest_create(request, **data)
            msg = _("Reachability Test %s was successfully created") \
                % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return reachabilitytest
        except Exception as e:
            exceptions.handle(request,
                              _("Failed to create reachability test. Info: "
                                "%s") % e.message)


class UpdateForm(CreateReachabilityTest):
    id = forms.CharField(max_length="36", widget=forms.HiddenInput())

    def __init__(self, request, *args, **kwargs):
        CreateReachabilityTest.__init__(self, request, *args, **kwargs)
        # set src_segment initial
        # if segment id/name is missing, this won't select the correct choice
        # user needs to reselect the segment
        if kwargs.get('initial') and kwargs.get('initial').get('src_segment'):
            src_seg = kwargs.get('initial').get('src_segment')
            for choice in self.fields['src_segment'].choices:
                if src_seg in choice:
                    self.initial['src_segment'] = str(choice[0])
                    break

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
            extract_src_tenant_and_segment(data)
            id = data['id']
            reachabilitytest = neutron \
                .reachabilitytest_update(request, id, **data)
            msg = _("Reachability Test %s was successfully updated") \
                % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return reachabilitytest
        except Exception as e:
            exceptions.handle(request,
                              _("Failed to update reachability test. Info: "
                                "%s") % e.message)


class RunQuickTestForm(forms.SelfHandlingForm):

    src_tenant = forms.ChoiceField(
        label=_("Source Tenant"),
        help_text=_("Test reachability for current tenant only."))

    src_segment = forms.ChoiceField(
        label=_("Source Segment"),
        help_text=_("Select a source segment."))

    def __init__(self, request, *args, **kwargs):
        super(RunQuickTestForm, self).__init__(request, *args, **kwargs)
        self.fields['src_tenant'].choices = populate_tenant_choices(request)
        self.fields['src_tenant'].widget.attrs['readonly'] = True
        self.fields['src_segment'].choices = populate_segment_choices(request)

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
            extract_src_tenant_and_segment(data)
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
            extract_src_tenant_and_segment(data)
            data['save_test'] = True
            reachabilityquicktest = neutron.reachabilityquicktest_update(
                request, request.user.project_id, **data)
            messages.success(
                request, _('Successfully saved quicktest %s') % data['name'])
            return reachabilityquicktest
        except Exception as e:
            messages.error(
                request, _('Failed to save quicktest %(name)s. Info: %(msg)s')
                % {'name': data['name'], 'msg': e.message})
