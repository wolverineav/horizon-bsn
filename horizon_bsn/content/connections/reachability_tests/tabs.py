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

from horizon import tabs

from django.utils.translation import ugettext_lazy as _


class DetailsTab(tabs.Tab):
    """Class to handle the data population of the test details views."""
    name = _("Details")
    slug = "details"
    template_name = \
        "project/connections/reachability_tests/_detail_overview.html"

    def get_context_data(self, request):
        reachabilitytest = self.tab_group.kwargs['reachabilitytest']
        return {"reachabilitytest": reachabilitytest}


class ReachabilityTestDetailTabs(tabs.TabGroup):
    slug = "reachability_test_details"
    tabs = (DetailsTab,)


class QuickDetailsTab(tabs.Tab):
    name = _("Quick Test Results")
    slug = "quick_details"
    template_name = \
        "project/connections/reachability_tests/_quick_detail_overview.html"

    def get_context_data(self, request):
        reachabilityquicktest = self.tab_group.kwargs['reachabilityquicktest']
        return {"reachabilityquicktest": reachabilityquicktest}


class QuickTestDetailTabs(tabs.TabGroup):
    slug = "quick_test_details"
    tabs = (QuickDetailsTab,)
