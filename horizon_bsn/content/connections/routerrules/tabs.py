# Copyright 2013
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

from django.utils.translation import ugettext_lazy as _

from horizon import tabs

from horizon_bsn.content.connections.routerrules import rulemanager
from horizon_bsn.content.connections.routerrules import tables as rrtbl


class RouterRulesTab(tabs.TableTab):
    table_classes = (rrtbl.RouterRulesTable,)
    name = _("Tenant Policies")
    slug = "routerrules"
    template_name = "horizon/common/_detail_table.html"

    def allowed(self, request):
        routers = []
        if 'routers' in self.tab_group.kwargs:
            routers = self.tab_group.kwargs['routers']
        for router in routers:
            try:
                # if any one router has router rules, return true
                getattr(router, 'router_rules')
                return True
            except Exception:
                continue
        return False

    def get_routerrules_data(self):
        routerrules = []
        routers = self.tab_group.kwargs['routers']
        for router in routers:
            try:
                rules = getattr(router, 'router_rules')
                # add router ID and name to the rules
                for rule in rules:
                    rule['router_id'] = router.id
                    rule['router_name'] = router.name_or_id
                    rule['id'] = '_'.join([str(rule['priority']),
                                           rule['router_name']])
                    routerrules.append(rule)
            except Exception:
                continue

        if not routerrules:
            return []
        routerrules = sorted(routerrules, key=lambda k: k['id'])
        return [rulemanager.RuleObject(r) for r in routerrules]
