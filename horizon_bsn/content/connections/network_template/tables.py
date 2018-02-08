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

from django.http import Http404
from django.utils.safestring import mark_safe
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon import messages
from horizon import tables
from horizon_bsn.api import neutron
from openstack_dashboard.api import heat

import logging

LOG = logging.getLogger(__name__)


class RemoveTemplateAction(tables.LinkAction):
    name = "remove"
    url = "horizon:project:connections:network_template:remove"
    classes = ("ajax-modal", "btn-danger")
    verbose_name = _("Remove Network Template Instance")

    def allowed(self, request, datum):
        try:
            assign = neutron\
                .networktemplateassignment_get(request,
                                               request.user.tenant_id)
            if assign:
                return True
        except Exception as e:
            LOG.debug(e)
            return False


class ApplyTemplateAction(tables.LinkAction):
    name = "apply"
    verbose_name = _("Apply Network Template")
    url = "horizon:project:connections:network_template:select"
    classes = ("ajax-modal", "btn-create")

    def allowed(self, request, datum):
        try:
            assign = neutron\
                .networktemplateassignment_get(request,
                                               request.user.tenant_id)
            if assign:
                return False
        except Exception:
            return True


class StacksUpdateRow(tables.Row):
    ajax = True

    def can_be_selected(self, datum):
        return datum.stack_status != 'DELETE_COMPLETE'

    def get_data(self, request, stack_id):
        assignment = None
        try:
            assignments = neutron.networktemplateassignment_list(
                request, **{'stack_id': stack_id})
            if not assignments:
                raise Exception('Network template associationg not found.')
            assignment = assignments[0]

            template = neutron.networktemplate_get(request,
                                                   assignment.template_id)

            stack = heat.stack_get(request, stack_id)
            resources = heat.resources_list(request, stack.stack_name)
            if stack.stack_status == 'DELETE_COMPLETE':
                # returning 404 to the ajax call removes the
                # row from the table on the ui
                raise Http404
            rowdata = {
                'template_id': assignment.template_id,
                'template_name': template.name,
                'stack_id': stack_id,
                'heat_stack_name': stack.stack_name,
                'description': stack.description,
                'status': stack.status,
                'stack_status': stack.stack_status,
                'stack_status_reason': stack.stack_status_reason,
                'resources': mark_safe('<br>'.join([
                    ('%s (%s)' % (r.resource_name,
                                  r.resource_type)).replace(' ', '&nbsp;')
                    for r in resources]))
            }
            return rowdata
        except Http404:
            try:
                # remove corresponding network template
                if assignment:
                    neutron.networktemplateassignment_delete(
                        request, assignment.id)
                msg = _('Removed template association for stack_id %s') % \
                    stack_id
                LOG.debug(msg)
                messages.success(request, msg)
            except Exception as e:
                msg = _('Network template association removal failed '
                        'due to %s') % e
                LOG.error(msg)
                messages.error(request, msg)
            raise
        except Exception as e:
            raise


class NetworkTemplateTable(tables.DataTable):
    STATUS_CHOICES = (
        ("Complete", True),
        ("Failed", False),
    )
    STACK_STATUS_DISPLAY_CHOICES = (
        ("init_in_progress", pgettext_lazy("current status of stack",
                                           u"Init In Progress")),
        ("init_complete", pgettext_lazy("current status of stack",
                                        u"Init Complete")),
        ("init_failed", pgettext_lazy("current status of stack",
                                      u"Init Failed")),
        ("create_in_progress", pgettext_lazy("current status of stack",
                                             u"Create In Progress")),
        ("create_complete", pgettext_lazy("current status of stack",
                                          u"Create Complete")),
        ("create_failed", pgettext_lazy("current status of stack",
                                        u"Create Failed")),
        ("delete_in_progress", pgettext_lazy("current status of stack",
                                             u"Delete In Progress")),
        ("delete_complete", pgettext_lazy("current status of stack",
                                          u"Delete Complete")),
        ("delete_failed", pgettext_lazy("current status of stack",
                                        u"Delete Failed")),
        ("update_in_progress", pgettext_lazy("current status of stack",
                                             u"Update In Progress")),
        ("update_complete", pgettext_lazy("current status of stack",
                                          u"Update Complete")),
        ("update_failed", pgettext_lazy("current status of stack",
                                        u"Update Failed")),
        ("rollback_in_progress", pgettext_lazy("current status of stack",
                                               u"Rollback In Progress")),
        ("rollback_complete", pgettext_lazy("current status of stack",
                                            u"Rollback Complete")),
        ("rollback_failed", pgettext_lazy("current status of stack",
                                          u"Rollback Failed")),
        ("suspend_in_progress", pgettext_lazy("current status of stack",
                                              u"Suspend In Progress")),
        ("suspend_complete", pgettext_lazy("current status of stack",
                                           u"Suspend Complete")),
        ("suspend_failed", pgettext_lazy("current status of stack",
                                         u"Suspend Failed")),
        ("resume_in_progress", pgettext_lazy("current status of stack",
                                             u"Resume In Progress")),
        ("resume_complete", pgettext_lazy("current status of stack",
                                          u"Resume Complete")),
        ("resume_failed", pgettext_lazy("current status of stack",
                                        u"Resume Failed")),
        ("adopt_in_progress", pgettext_lazy("current status of stack",
                                            u"Adopt In Progress")),
        ("adopt_complete", pgettext_lazy("current status of stack",
                                         u"Adopt Complete")),
        ("adopt_failed", pgettext_lazy("current status of stack",
                                       u"Adopt Failed")),
        ("snapshot_in_progress", pgettext_lazy("current status of stack",
                                               u"Snapshot In Progress")),
        ("snapshot_complete", pgettext_lazy("current status of stack",
                                            u"Snapshot Complete")),
        ("snapshot_failed", pgettext_lazy("current status of stack",
                                          u"Snapshot Failed")),
        ("check_in_progress", pgettext_lazy("current status of stack",
                                            u"Check In Progress")),
        ("check_complete", pgettext_lazy("current status of stack",
                                         u"Check Complete")),
        ("check_failed", pgettext_lazy("current status of stack",
                                       u"Check Failed")),
    )

    template_name = tables.Column("template_name",
                                  verbose_name=_("Template Name"))

    stack_id = tables.Column("stack_id", hidden=True)

    heat_stack_name = tables.Column("heat_stack_name",
                                    verbose_name=_("Heat Stack Name"))

    description = tables.Column("description", verbose_name=_("Description"))

    # status = tables.Column("status", verbose_name=_("Status"))

    resources = tables.Column("resources", verbose_name=_("Resources"))

    status = tables.Column("status",
                           hidden=True,
                           status=True,
                           status_choices=STATUS_CHOICES)

    stack_status = tables.Column("stack_status",
                                 verbose_name=_("Status"),
                                 display_choices=STACK_STATUS_DISPLAY_CHOICES)

    def get_object_id(self, template_stack):
        return template_stack['stack_id']

    class Meta(object):
        multi_select = False
        name = "networktemplate"
        verbose_name = _("Network Template")
        table_actions = (ApplyTemplateAction, RemoveTemplateAction)
        status_columns = ["status", ]
        row_class = StacksUpdateRow
        # row_actions = tuple()


class DeleteTemplateAction(tables.DeleteAction):
    data_type_singular = _("Network Template")
    data_type_plural = _("Network Templates")

    def delete(self, request, obj_id):
        try:
            neutron.networktemplate_delete(request, obj_id)
        except Exception as e:
            LOG.info(str(e))
            messages.error(
                request, _("Unable to delete template. Template may "
                           "be in use by a tenant."))

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Network Template",
            u"Delete Network Templates",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Network Template",
            u"Deleted Network Templates",
            count
        )


class CreateTemplateAction(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Network Template")
    url = "horizon:admin:connections:network_template_admin:create"
    classes = ("ajax-modal", "btn-create")


class NetworkTemplateAdminTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_("Template ID"), hidden=True)
    name = tables.Column(
        "name", verbose_name=_("Name"),
        link="horizon:admin:connections:network_template_admin:detail")

    class Meta(object):
        name = "networktemplate_admin"
        verbose_name = _("Network Template Administration")
        table_actions = (CreateTemplateAction, DeleteTemplateAction)
        row_actions = (DeleteTemplateAction,)
