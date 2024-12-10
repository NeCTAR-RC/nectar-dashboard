from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
import horizon
from horizon import forms
from horizon import tables
from openstack_dashboard.dashboards.project.instances import (
    tables as instance_tables,
)
from openstack_dashboard.dashboards.project.instances import views
from trove_dashboard.content.databases.workflows import create_instance

try:
    from varroa_dashboard.api import security

    project_dashboard = horizon.get_dashboard('project')
    security_panel = project_dashboard.get_panel('security')
    varroa_enabled = True
except Exception:
    varroa_enabled = False


class TroveSetInstanceDetailsAction(create_instance.SetInstanceDetailsAction):
    volume_type = forms.ChoiceField(
        label=_("Volume Type"), required=False, widget=forms.HiddenInput()
    )

    class Meta:
        name = _("Details")
        help_text_template = "project/databases/_launch_details_help.html"


create_instance.SetInstanceDetails.action_class = TroveSetInstanceDetailsAction

if varroa_enabled:

    def render_risks(instance):
        has_risks = security.get_security_risks(
            instance.request, resource_id=instance.id
        )

        if has_risks:
            security_url = reverse('horizon:project:security:index')
            risk_url = f'{security_url}#{instance.id}'
            icon_classes = (
                "fa fa-exclamation-circle text-danger text-decoration-none"
            )
            help_tooltip = _(
                "This instance has security risks. Click to learn more."
            )
            locked_status = (
                f'<a href="{risk_url}" data-toggle="tooltip" title="{help_tooltip}" class="{icon_classes}">'
                '</a>'
            )
        else:
            locked_status = ''
        return mark_safe(locked_status)

    class NectarInstancesTable(instance_tables.InstancesTable):
        risks = tables.Column(render_risks, verbose_name="", sortable=False)

        class Meta(instance_tables.InstancesTable.Meta):
            columns = (
                'name',
                'risks',
                'image_name',
                'ip',
                'flavor',
                'keypair',
                'status',
                'locked',
                'az',
                'task',
                'state',
                'created',
            )

    views.IndexView.table_class = NectarInstancesTable
