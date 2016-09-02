# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""API over the neutron service.
"""

from django.views import generic

from openstack_dashboard.api.rest import urls
from openstack_dashboard.api.rest import utils as rest_utils

from horizon_bsn.api import neutron as bsnneutron

from openstack_dashboard.api import heat
from openstack_dashboard.api import neutron

from horizon_bsn.content.connections.tabs import get_stack_topology

import logging

LOG = logging.getLogger(__name__)

"""
Three of the list API calls (reachabilitytest, networktemplate,
networktemplateassignment) return dictionaries rather than objects.
This is because the list_function on the Javascript side that is
part of the upstream Horizon framework doesn't play nice w/ just
returning objects. However, the other API methods return values to
newly written functions, not from upstream. The only list call
different is router_rules, because router_rules rely on updating
the router, and there are no separate constructs for router_rules
on the neutron side
"""

##################################################################
# REACHABILITY TESTS
##################################################################


@urls.register
class ReachabilityTest(generic.View):
    """API for BSN Neutron Reachability Tests"""
    url_regex = \
        r'neutron/reachabilitytests/(?P<test_id>[^/]+|default)/$'

    @rest_utils.ajax()
    def patch(self, request, test_id):
        result = bsnneutron.\
            reachabilitytest_update(request, test_id, run_test=True)
        return result

    @rest_utils.ajax()
    def delete(self, request, test_id):
        result = bsnneutron.reachabilitytest_delete(request, test_id)
        return result


@urls.register
class ReachabilityTests(generic.View):
    """API for BSN Neutron Reachability Tests"""
    url_regex = r'neutron/reachabilitytests/$'

    @rest_utils.ajax()
    def get(self, request):
        result = bsnneutron.reachabilitytest_list(
            request,
            **{'tenant_id': request.user.project_id})
        return {'items': [n.to_dict() for n in result]}

    @rest_utils.ajax()
    def post(self, request):
        result = bsnneutron.reachabilitytest_create(request, **request.DATA)
        return result


@urls.register
class ReachabilityQuickTest(generic.View):
    """API for BSN Neutron Reachability Tests"""
    url_regex = r'neutron/reachabilityquicktest/$'

    @rest_utils.ajax()
    def post(self, request):
        result = bsnneutron.\
            reachabilityquicktest_create(request, **request.DATA)
        return result

    @rest_utils.ajax()
    def get(self, request):
        result = bsnneutron.\
            reachabilityquicktest_get(request, request.user.project_id)
        return result

    @rest_utils.ajax()
    def patch(self, request):
        result = bsnneutron.\
            reachabilityquicktest_update(request,
                                         request.user.project_id,
                                         **request.DATA)
        return result

##################################################################
# NETWORK TEMPLATE ASSIGNMENT
##################################################################


@urls.register
class HeatStack(generic.View):
    """API for Router_get"""
    url_regex = r'heat/stack/(?P<stack_id>[^/]+|default)/$'

    @rest_utils.ajax()
    def delete(self, request, stack_id):
        result = heat.stack_delete(request, stack_id)
        return result

    @rest_utils.ajax()
    def get(self, request, stack_id):
        result = heat.stack_get(request, stack_id)
        return result.stack_status


@urls.register
class HeatStacks(generic.View):
    """API for Router_get"""
    url_regex = r'heat/stack/$'

    @rest_utils.ajax()
    def post(self, request):
        result = heat.stack_create(request, **request.DATA)
        return result


@urls.register
class HeatTemplateValidate(generic.View):
    """API for BSN Neutron Network Template Assignment"""
    url_regex = r'heat/templatevalidate/$'

    @rest_utils.ajax()
    def post(self, request):
        result = heat.template_validate(request, template=request.DATA['body'])
        return result


@urls.register
class NetworkTemplateAssignment(generic.View):
    """API for BSN Neutron Network Template Assignment"""
    url_regex = \
        r'neutron/networktemplateassignment/(?P<assignment_id>[^/]+|default)/$'

    @rest_utils.ajax()
    def delete(self, request, assignment_id):
        result = bsnneutron.\
            networktemplateassignment_delete(request, assignment_id)
        return result


@urls.register
class NetworkTemplateAssignments(generic.View):
    """API for BSN Neutron Network Template Assignment"""
    url_regex = r'neutron/networktemplateassignment/$'

    @rest_utils.ajax()
    def post(self, request):
        result = bsnneutron.\
            networktemplateassignment_create(request, **request.DATA)
        return result

    @rest_utils.ajax()
    def patch(self, request):
        result = bsnneutron.\
            networktemplateassignment_update(
                request,
                request.user.project_id,
                **{'stack_id': request.DATA['stack_id']})
        return result

    @rest_utils.ajax()
    def get(self, request):
        try:
            topology = get_stack_topology(request)
            if not topology.get('assign'):
                return []
            tabledata = {
                'id': topology['template'].id,
                'name': topology['template'].name,
                'stack_id': topology['stack'].id,
                'heat_stack_name': topology['stack'].stack_name,
                'description': topology['stack'].description,
                'status': topology['stack'].status,
                'stack_status': topology['stack'].stack_status,
                'stack_status_reason': topology['stack'].stack_status_reason,
                'resources': '<br>'.join([
                    ('%s (%s)' % (r.resource_name,
                                  r.resource_type))
                    for r in topology['stack_resources']])
            }
            return {'items': [tabledata]}
        except Exception:
            return []

##################################################################
# NETWORK TEMPLATE
##################################################################


@urls.register
class NetworkTemplate(generic.View):
    """API for BSN Neutron Network Template"""
    url_regex = \
        r'neutron/networktemplate/(?P<template_id>[^/]+|default)/$'

    @rest_utils.ajax()
    def get(self, request, template_id):
        result = bsnneutron.networktemplate_get(request, template_id)
        return result

    @rest_utils.ajax()
    def patch(self, request, template_id):
        result = bsnneutron.\
            networktemplate_update(request, template_id, **request.DATA)
        return result

    @rest_utils.ajax()
    def delete(self, request, template_id):
        result = bsnneutron.networktemplate_delete(request, template_id)
        return result


@urls.register
class NetworkTemplates(generic.View):
    """API for BSN Neutron Network Template"""
    url_regex = r'neutron/networktemplate/$'

    @rest_utils.ajax()
    def post(self, request):
        result = bsnneutron.networktemplate_create(request, **request.DATA)
        return result

    @rest_utils.ajax()
    def get(self, request):
        result = bsnneutron.networktemplate_list(
            request,
            **{'tenant_id': request.user.project_id})
        return {'items': [n.to_dict() for n in result]}

##################################################################
# ROUTER RULES
##################################################################


@urls.register
class Router(generic.View):
    """API for Router_get"""
    url_regex = r'neutron/router/$'

    @rest_utils.ajax()
    def get(self, request):
        result = neutron.router_list(request)[0]
        return result

    @rest_utils.ajax()
    def patch(self, request):
        body = {'router_rules': request.DATA['router_rules']}
        result = neutron.router_update(request, request.DATA['id'], **body)
        return result
