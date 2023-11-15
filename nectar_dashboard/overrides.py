# Currently no overrides

from django.utils.translation import gettext_lazy as _
from horizon import forms

from trove_dashboard.content.databases.workflows import create_instance


class TroveSetInstanceDetailsAction(create_instance.SetInstanceDetailsAction):
    volume_type = forms.ChoiceField(
        label=_("Volume Type"),
        required=False,
        widget=forms.HiddenInput())

    class Meta(object):
        name = _("Details")
        help_text_template = "project/databases/_launch_details_help.html"


create_instance.SetInstanceDetails.action_class = TroveSetInstanceDetailsAction
