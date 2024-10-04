# The slug of the panel to be added to HORIZON_CONFIG. Required.
PANEL = 'reset-password'
# The slug of the dashboard the PANEL associated with. Required.
PANEL_DASHBOARD = 'settings'
# The slug of the panel group the PANEL is associated with.
PANEL_GROUP = 'default'

# Python panel class of the PANEL to be added.
ADD_PANEL = 'nectar_dashboard.reset_password.panel.PasswordPanel'

# A list of applications to be added to INSTALLED_APPS.
ADD_INSTALLED_APPS = [
    'nectar_dashboard.reset_password',
]
