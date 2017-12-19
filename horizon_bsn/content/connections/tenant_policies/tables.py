# Copyright 2013,  Big Switch Networks, Inc
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

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon import tables
from horizon_bsn.api import neutron

LOG = logging.getLogger(__name__)


class RandomFilterAction(tables.FilterAction):
    def filter(self, table, policies, filter_string):
        """Naive case-insentitive search."""
        q = filter_string.lower()
        return [policy for policy in policies
                if q in str(policy.to_dict())]


class AddTenantPolicy(tables.LinkAction):
    name = "create"
    verbose_name = _("Add Tenant Policy")
    url = "horizon:project:connections:tenant_policies:create"
    classes = ("ajax-modal", "btn-create")
    icon = "plus"


class RemoveTenantPolicy(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Tenant Policy",
            u"Delete Tenant Policies",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Tenant Policy",
            u"Deleted Tenant Policies",
            count
        )

    failure_url = 'horizon:project:connections:index'

    def delete(self, request, id):
        neutron.tenantpolicy_delete(request, id)


class TenantPoliciesTable(tables.DataTable):
    id = tables.Column("id", hidden=True)
    priority = tables.Column("priority", verbose_name=_("Priority"))

    source = tables.Column("source", verbose_name=_("Source CIDR"))
    source_port = tables.Column("source_port", verbose_name=_("Source Port"))
    destination = tables.Column("destination",
                                verbose_name=_("Destination CIDR"))
    destination_port = tables.Column("destination_port",
                                     verbose_name=_("Destination Port"))
    protocol = tables.Column("protocol", verbose_name=_("Protocol"))
    action = tables.Column("action", verbose_name=_("Action"))
    nexthops = tables.Column("nexthops", verbose_name=_("Next Hops"))

    def get_object_display(self, rule):
        return ("Policy %(priority)s (%(action)s) "
                "%(source)s %(source_port)s -- %(destination)s "
                "%(destination_port)s %(protocol)s") % rule

    class Meta(object):
        name = "tenantpolicies"
        verbose_name = _("Tenant Policies")
        table_actions = (AddTenantPolicy, RemoveTenantPolicy,
                         RandomFilterAction,)
        row_actions = (RemoveTenantPolicy,)
