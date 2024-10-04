# The name of the dashboard to be added to HORIZON['dashboards']. Required.
PANEL_DASHBOARD = 'identity'

PANEL_GROUP = 'default'

PANEL = 'lookup'

# If set to True, this dashboard will not be added to the settings.
DISABLED = False


# Python panel class of the PANEL to be added.
ADD_PANEL = 'nectar_dashboard.user_info.lookup.panel.UserLookupPanel'

# A list of applications to be added to INSTALLED_APPS.
ADD_INSTALLED_APPS = [
    'nectar_dashboard.user_info',
    'nectar_dashboard.user_info.lookup',
]

AUTO_DISCOVER_STATIC_FILES = False

ADD_SCSS_FILES = [
    'rcportal/scss/nectar.scss',
    'rcportal/scss/bootstrap-toggle.scss',
]
