import logging

from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
import horizon
from horizon import forms
from horizon import tables
from openstack_dashboard.api.rest import utils as rest_utils
from openstack_dashboard.dashboards.project.instances import (
    tables as instance_tables,
)
from openstack_dashboard.dashboards.project.instances import views
from trove_dashboard.content.databases.workflows import create_instance

LOG = logging.getLogger(__name__)

security = None
try:
    from varroa_dashboard.api import security

    project_dashboard = horizon.get_dashboard('project')
    security_panel = project_dashboard.get_panel('security')
    varroa_enabled = True
except Exception:
    varroa_enabled = False

try:
    from magnum_ui.api.rest import magnum as magnum_rest

    magnum_ui_enabled = True
except Exception:
    magnum_ui_enabled = False


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


def _cluster_security_risks(request):
    """Map cluster id to the project's varroa security risks.

    Returns an empty mapping when varroa cannot be reached; the
    clusters panel must keep working without it.
    """
    risks = {}
    if security is None:
        return risks
    try:
        results = security.get_security_risks(request, resource_type='cluster')
    except Exception:
        LOG.exception("Failed to fetch security risks from varroa")
        return risks
    for risk in results:
        risks.setdefault(risk.resource_id, []).append(
            {
                'id': risk.id,
                'type': {
                    'name': risk.type.name,
                    'display_name': str(risk.type),
                    'description': risk.type.description,
                    'help_url': getattr(risk.type, 'help_url', None),
                },
            }
        )
    return risks


@rest_utils.ajax()
def _clusters_get_with_risks(self, request):
    """Replacement for magnum-ui's Clusters.get list view.

    Same response, but each cluster carries the varroa security risks
    reported against it (e.g. an EOL Kubernetes version) so the
    clusters table can show a warning column. The column is added by
    nectar_dashboard/cluster_risks (see the
    _9500_cluster_security_risks enabled file).
    """
    result = magnum_rest.magnum.cluster_list(request)
    risks = _cluster_security_risks(request)
    items = []
    for cluster in result:
        item = magnum_rest.change_to_id(cluster.to_dict())
        item['security_risks'] = risks.get(item['id'], [])
        items.append(item)
    return {'items': items}


if varroa_enabled and magnum_ui_enabled:
    magnum_rest.Clusters.get = _clusters_get_with_risks
