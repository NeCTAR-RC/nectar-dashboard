from django.utils.translation import gettext_lazy as _

import horizon


class PasswordPanel(horizon.Panel):
    name = _("Reset Password")
    slug = 'reset-password'
