# Currently no overrides

from django.utils.translation import ugettext_lazy as _

from horizon import forms

from openstack_dashboard.dashboards.project.volumes import views as volume_views
from openstack_dashboard.dashboards.project.volumes import forms as volume_forms

class NectarVolumeCreateForm(volume_forms.CreateForm):

    type = forms.ChoiceField(
        label=_("Type"),
        required=False,
        widget=forms.HiddenInput())


volume_views.CreateView.form_class = NectarVolumeCreateForm
