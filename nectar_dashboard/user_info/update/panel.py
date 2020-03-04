from django.utils.translation import ugettext_lazy as _

import horizon


class UserUpdatePanel(horizon.Panel):
    name = _("User Info Update")
    slug = 'update'
    index_url_name = 'edit-self'
