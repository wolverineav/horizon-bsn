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

from django.utils.translation import ugettext_lazy as _
from horizon import messages
from openstack_dashboard.api import neutron as api

LOG = logging.getLogger(__name__)


class RuleObject(dict):
    def __init__(self, rule):
        # unique identifier is priority_routerid
        rule['id'] = '_'.join([str(rule['priority']),
                               rule['router_id']])
        super(RuleObject, self).__init__(rule)
        # Horizon references priority property for table operations
        self.id = rule['id']
        # Flatten into csv for display
        self.nexthops = ','.join(rule['nexthops'])


def is_rule_in_set(rule, rule_list):
    """Check if the given rule is present in the rule_list

    :param rule_list: list of existing rules in dictionary format
    :param rule: new rule to be added
    :return boolean:
    """
    for old_rule in rule_list:
        if rule['source'] == old_rule['source']\
                and rule['destination'] == old_rule['destination']\
                and rule['action'] == old_rule['action']\
                and rule['priority'] == old_rule['priority']:
            return True
    return False


def get_rule_diff(old_ruleset, new_ruleset):
    added_rules = [rule for rule in new_ruleset
                   if not is_rule_in_set(rule, old_ruleset)]
    deleted_rules = [rule for rule in old_ruleset
                     if not is_rule_in_set(rule, new_ruleset)]
    return deleted_rules, added_rules


def popup_messages(request, old_ruleset, new_ruleset):
    deleted_rules, added_rules = get_rule_diff(old_ruleset, new_ruleset)
    if deleted_rules:
        del_msg = _('Removed router policies: %s') % deleted_rules
        LOG.debug(del_msg)
        messages.warning(request, del_msg)
    if added_rules:
        add_msg = _('Added router policies: %s') % added_rules
        LOG.debug(add_msg)
        messages.success(request, add_msg)
    if not deleted_rules and not added_rules:
        no_op_msg = _('No change in policies, superset policy exists.')
        LOG.debug(no_op_msg)
        messages.warning(request, no_op_msg)


def routerrule_list(request, router_id):
    if ('routers_dict' in request.META
            and router_id in request.META['routers_dict']):
        router = request.META['routers_dict'][router_id]
    else:
        router = api.router_get(request, router_id)
    try:
        rules = router.router_rules
    except AttributeError:
        return (False, [])
    return (True, rules)


def remove_rules(request, rule_id):
    LOG.debug("remove_rules(): rule_id=%s", rule_id)
    prio_routerid = rule_id.split('_')
    priority = prio_routerid[0]
    router_id = prio_routerid[1]
    supported, currentrules = routerrule_list(request, router_id)
    if not supported:
        LOG.error(_("router policies not supported by router %s") % router_id)
        return
    newrules = []
    for oldrule in currentrules:
        if oldrule['priority'] != int(priority):
            newrules.append(oldrule)
    body = {'router_rules': format_for_api(newrules)}
    new = api.router_update(request, router_id, **body)
    if ('routers_dict' in request.META
            and router_id in request.META['routers_dict']):
        request.META['routers_dict'][router_id] = new
    popup_messages(request, currentrules, new.router_rules)
    return new


def add_rule(request, router_id, newrule):
    body = {'router_rules': []}
    supported, currentrules = routerrule_list(request, router_id)
    if not supported:
        LOG.error(_("router policies not supported by router %s") % router_id)
        return
    body['router_rules'] = format_for_api([newrule] + currentrules)
    new = api.router_update(request, router_id, **body)
    request.META['routers_dict'][router_id] = new
    popup_messages(request, currentrules, new.router_rules)
    return new


def format_for_api(rules):
    apiformrules = []
    for r in rules:
        # make a copy so we don't damage original dict in rules
        flattened = r.copy()
        # nexthops should only be present if there are nexthop addresses
        if 'nexthops' in flattened:
            cleanednh = [nh.strip()
                         for nh in flattened['nexthops']
                         if nh.strip()]
            if cleanednh:
                flattened['nexthops'] = '+'.join(cleanednh)
            else:
                del flattened['nexthops']
        apiformrules.append(flattened)
    return apiformrules
