from django.utils.translation import ugettext_lazy as _

import horizon


class PasswordPanel(horizon.Panel):
    name = _("Reset Password")
    slug = 'reset-password'
