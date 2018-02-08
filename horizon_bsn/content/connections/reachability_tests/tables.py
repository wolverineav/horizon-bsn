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

from horizon import exceptions
from horizon import tables
from horizon.utils import filters

from django.template.defaultfilters import title
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon_bsn.api import neutron


class DeleteReachabilityTests(tables.DeleteAction):
    data_type_singular = _("Test")
    data_type_plural = _("Tests")

    def delete(self, request, id):
        try:
            neutron.reachabilitytest_delete(request, id)
        except Exception:
            exceptions.handle(request,
                              _("Failed to update reachability test"))

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Reachability Test",
            u"Delete Reachability Tests",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Reachability Test",
            u"Deleted Reachability Tests",
            count
        )


class CreateReachabilityTest(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Test")
    url = "horizon:project:connections:reachability_tests:create"
    classes = ("ajax-modal", "btn-create")


class RunQuickTest(tables.LinkAction):
    name = "quick_test"
    verbose_name = _("Quick Test")
    url = "horizon:project:connections:reachability_tests:run"
    classes = ("ajax-modal", "btn-edit")


class ReachabilityTestFilterAction(tables.FilterAction):

    def filter(self, table, reachabilitytests, filter_string):
        """Naive case-insentitive search."""
        q = filter_string.lower()
        return [reachabilitytest for reachabilitytest in reachabilitytests
                if q in reachabilitytest.name.lower()]


class RunTest(tables.BatchAction):
    name = "run"
    data_type_singular = _("Test")
    classes = ("btn-edit", )

    def action(self, request, id):
        neutron.reachabilitytest_update(request, id, **{'run_test': True})

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Run Reachability Test",
            u"Run Reachability Tests",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Running Reachability Test",
            u"Running Reachability Tests",
            count
        )


class UpdateTest(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Test")
    url = "horizon:project:connections:reachability_tests:update"
    classes = ("ajax-modal", "btn-edit")


STATUS_DISPLAY_CHOICES = (
    ("pass", _("PASS")),
    ("pending", _("PENDING")),
    ("fail", _("FAIL")),
    ("-", _("-")),
    ('', _("-")),
)

STATUS_CHOICES = (
    ("pass", True),
    ("-", None),
    ('', None),
    ("pending", None),
    ("fail", False),
)


class ReachabilityTestsTable(tables.DataTable):
    id = tables.Column("id", hidden=True)
    name = tables.Column("name", verbose_name=_("Name"))
    src_tenant_name = tables.Column(
        "src_tenant_name", verbose_name="Source Tenant")
    src_segment_name = tables.Column(
        "src_segment_name", verbose_name="Source Segment")
    src_ip = tables.Column("src_ip", verbose_name=_("Source IP"))
    dst_ip = tables.Column("dst_ip", verbose_name=_("Destination IP"))
    test_time = tables.Column(
        "test_time",
        link=("horizon:project:connections:reachability_tests:detail"),
        verbose_name=_("Last Run"))
    status = tables.Column(
        "test_result", filters=(title, filters.replace_underscores),
        verbose_name=_("Status"), status_choices=STATUS_CHOICES,
        display_choices=STATUS_DISPLAY_CHOICES)

    class Meta(object):
        name = "reachabilitytests"
        verbose_name = _("Reachability Tests")
        table_actions = (CreateReachabilityTest, RunQuickTest,
                         DeleteReachabilityTests, ReachabilityTestFilterAction)
        row_actions = (RunTest, UpdateTest, DeleteReachabilityTests)
