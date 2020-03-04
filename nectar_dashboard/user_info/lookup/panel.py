from django.utils.translation import ugettext_lazy as _

import horizon


class UserLookupPanel(horizon.Panel):
    name = _("User Info Lookup")
    slug = 'lookup'
    index_url_name = 'lookup'
