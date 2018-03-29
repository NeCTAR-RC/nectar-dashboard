# Currently no overrides

from django.utils.translation import ugettext_lazy as _
from horizon import forms

from trove_dashboard.content.databases.workflows import create_instance

from openstack_dashboard.dashboards.project.volumes import views as volume_views # noqa
from openstack_dashboard.dashboards.project.volumes import forms as volume_forms # noqa


class NectarVolumeCreateForm(volume_forms.CreateForm):

    type = forms.ChoiceField(
        label=_("Type"),
        required=False,
        widget=forms.HiddenInput())


volume_views.CreateView.form_class = NectarVolumeCreateForm


class TroveSetInstanceDetailsAction(create_instance.SetInstanceDetailsAction):
    volume_type = forms.ChoiceField(
        label=_("Volume Type"),
        required=False,
        widget=forms.HiddenInput())

    class Meta(object):
        name = _("Details")
        help_text_template = "project/databases/_launch_details_help.html"


create_instance.SetInstanceDetails.action_class = TroveSetInstanceDetailsAction
