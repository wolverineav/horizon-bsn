# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from horizon import tabs

from horizon_bsn.api import neutron
from horizon_bsn.content.connections.network_template.tables \
    import NetworkTemplateAdminTable
from horizon_bsn.content.connections.network_template.tables \
    import NetworkTemplateTable
from horizon_bsn.content.connections.reachability_tests.tables \
    import ReachabilityTestsTable
from horizon_bsn.content.connections.routerrules import tabs as rr_tabs

import json

from openstack_dashboard.api import heat

LOG = logging.getLogger(__name__)


class NetworkTemplateAdminTab(tabs.TableTab):
    table_classes = (NetworkTemplateAdminTable,)
    name = _("Network Template Admin")
    slug = "network_template_tab_admin"
    template_name = "horizon/common/_detail_table.html"

    def allowed(self, request):
        return (self.request.path_info.startswith('/admin/') and
                super(NetworkTemplateAdminTab, self).allowed(request))

    def get_networktemplate_admin_data(self):
        try:
            networktemplates = neutron.networktemplate_list(self.request, **{})
            return networktemplates
        except Exception:
            return []


def get_stack_topology(request):
    try:
        assign = neutron.networktemplateassignment_get(
            request, request.user.tenant_id)
        networktemplate = neutron.networktemplate_get(
            request, assign.template_id)
    except Exception:
        return {"network_entities": "{}",
                "network_connections": "{}"}

    hc = heat.heatclient(request)
    # we only want the one that matches the network template
    stacks = [s for s in hc.stacks.list(tenant_id=request.user.tenant_id)
              if s.id == assign.stack_id]
    if not stacks:
        # leftover association, delete the assignment
        neutron.networktemplateassignment_delete(request,
                                                 request.user.tenant_id)
        return {"network_entities": "",
                "network_connections": ""}
    resources = hc.resources.list(assign.stack_id)
    entities = {}
    connections = []
    for res in resources:
        if res.resource_type in ('OS::Neutron::Router', 'OS::Neutron::Subnet'):
            entities[res.physical_resource_id] = {
                'properties': {'name': res.physical_resource_id}
            }
        if res.resource_type == 'OS::Neutron::RouterInterface':
            connections.append({
                'source': res.physical_resource_id.split(':subnet_id=')[0],
                'destination':
                    res.physical_resource_id.split('subnet_id=')[-1],
                'expected_connection': 'forward'
            })
    resp = {'template': networktemplate,
            'assign': assign,
            'network_entities': json.dumps(entities),
            'network_connections': json.dumps(connections),
            'stack_resources': resources,
            'stack': stacks[0]}
    return resp


def is_heat_available(request):
    try:
        heat.heatclient(request)
        return True
    except Exception:
        return False


class NetworkTemplateTab(tabs.TableTab):
    table_classes = (NetworkTemplateTable,)
    name = _("Network Template")
    slug = "network_template_tab"
    template_name = "horizon/common/_detail_table.html"

    def allowed(self, request):
        # don't show tab to tenants if heat isn't installed
        if not is_heat_available(request):
            return False
        # don't show the regular template tab to admins
        return (not request.path_info.startswith('/admin/')
                and super(NetworkTemplateTab, self).allowed(request))

    def get_networktemplate_data(self):
        try:
            topology = get_stack_topology(self.request)
            if not topology.get('assign'):
                return []
            tabledata = {
                'template_id': topology['template'].id,
                'template_name': topology['template'].name,
                'stack_id': topology['stack'].id,
                'heat_stack_name': topology['stack'].stack_name,
                'description': topology['stack'].description,
                'status': topology['stack'].status,
                'stack_status': topology['stack'].stack_status,
                'stack_status_reason': topology['stack'].stack_status_reason,
                'resources': mark_safe('<br>'.join([
                    ('%s (%s)' % (r.resource_name,
                                  r.resource_type)).replace(' ', '&nbsp;')
                    for r in topology['stack_resources']]))
            }
            return [tabledata]
        except Exception:
            return []


class ReachabilityTestsTab(tabs.TableTab):
    table_classes = (ReachabilityTestsTable,)
    name = _("Reachability Tests")
    slug = "reachabilitytest_tab"
    template_name = "horizon/common/_detail_table.html"

    def allowed(self, request):
        # don't show the regular tab to admins
        return (not request.path_info.startswith('/admin/')
                and super(ReachabilityTestsTab, self).allowed(request))

    def get_reachabilitytests_data(self):
        try:
            reachabilitytests = neutron.reachabilitytest_list(
                self.request, **{'tenant_id': self.request.user.project_id})
            return reachabilitytests
        except Exception:
            return []


class ReachabilityTestsAdminTab(tabs.TableTab):
    table_classes = (ReachabilityTestsTable,)
    name = _("Reachability Tests")
    slug = "reachabilitytest_admin_tab"
    template_name = "horizon/common/_detail_table.html"

    def allowed(self, request):
        return (self.request.path_info.startswith('/admin/') and
                super(ReachabilityTestsAdminTab, self).allowed(request))

    def get_reachabilitytests_data(self):
        try:
            reachabilitytests = neutron.reachabilitytest_list(self.request,
                                                              **{})
            return reachabilitytests
        except Exception:
            return []


class ConnectionsTabs(tabs.TabGroup):
    slug = "connections_tabs"
    # TODO(kevinbenton): re-enabled top talkers once implemented
    # tabs = (NetworkTemplateTab, ReachabilityTestsTab, TopTalkersTab)
    sticky = True
    tabs = (ReachabilityTestsTab, ReachabilityTestsAdminTab,
            NetworkTemplateTab, NetworkTemplateAdminTab,
            rr_tabs.RouterRulesTab)
