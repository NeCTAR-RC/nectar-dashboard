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

    def prepare_source_fields_if_snapshot_specified(self, request):
        try:
            snapshot = self.get_snapshot(request,
                                         request.GET["snapshot_id"])
            self.fields['name'].initial = snapshot.name
            self.fields['size'].initial = snapshot.size
            self.fields['snapshot_source'].choices = ((snapshot.id,
                                                       snapshot),)
            try:
                # Set the volume type from the original volume
                orig_volume = cinder.volume_get(request,
                                                snapshot.volume_id)
            except Exception:
                pass
            self.fields['size'].help_text = (
                _('Volume size must be equal to or greater than the '
                  'snapshot size (%sGiB)') % snapshot.size)
            self.fields['type'].widget = forms.widgets.HiddenInput()
            del self.fields['image_source']
            del self.fields['volume_source']
            del self.fields['volume_source_type']
            del self.fields['availability_zone']
            
        except Exception:
            exceptions.handle(request,
                              _('Unable to load the specified snapshot.'))

    def prepare_source_fields_if_volume_specified(self, request):
        self.fields['availability_zone'].choices = \
                                                   availability_zones(request)
        volume = None
        try:
            volume = self.get_volume(request, request.GET["volume_id"])
        except Exception:
            msg = _('Unable to load the specified volume. %s')
            exceptions.handle(request, msg % request.GET['volume_id'])
            
        if volume is not None:
            self.fields['name'].initial = volume.name
            self.fields['description'].initial = volume.description
            min_vol_size = volume.size
            size_help_text = (_('Volume size must be equal to or greater '
                                'than the origin volume size (%sGiB)')
                              % volume.size)
            self.fields['size'].initial = min_vol_size
            self.fields['size'].help_text = size_help_text
            self.fields['volume_source'].choices = ((volume.id, volume),)
            del self.fields['snapshot_source']
            del self.fields['image_source']
            del self.fields['volume_source_type']


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
