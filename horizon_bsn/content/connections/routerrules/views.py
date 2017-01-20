# Copyright 2013, Big Switch Networks
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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon.utils import memoized

from horizon_bsn.content.connections.routerrules import forms as rrforms

from openstack_dashboard import api


LOG = logging.getLogger(__name__)


class AddRouterRuleView(forms.ModalFormView):
    form_class = rrforms.AddRouterRule
    template_name = 'project/connections/routerrules/create.html'
    url = 'horizon:project:connections:index'
    page_title = _("Add Router Policy")

    def get_success_url(self):
        return reverse(self.url)

    @memoized.memoized_method
    def get_object(self):
        try:
            routers = api.neutron.router_list(
                self.request, **{'tenant_id': self.request.user.project_id})
            return routers
        except Exception:
            redirect = reverse(self.url)
            msg = _('Unable to retrieve router(s) for the current tenant.')
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(AddRouterRuleView, self).get_context_data(**kwargs)
        context['routers'] = self.get_object()
        return context

    def get_initial(self, **kwargs):
        routers = self.get_object()
        # store the router in the request so the rule manager doesn't have
        # to request it again from the API
        routers_dict = {}
        for router in routers:
            routers_dict[router.id] = router
        self.request.META['routers_dict'] = routers_dict
        return {}
