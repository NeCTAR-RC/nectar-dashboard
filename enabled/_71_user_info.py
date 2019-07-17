# The name of the dashboard to be added to HORIZON['dashboards']. Required.
DASHBOARD = 'user-info'

# If set to True, this dashboard will not be added to the settings.
DISABLED = False

# A list of applications to be added to INSTALLED_APPS.
ADD_INSTALLED_APPS = [
    'nectar_dashboard.user_info',
    'nectar_dashboard.user_info.lookup',
    'nectar_dashboard.user_info.update',
]

AUTO_DISCOVER_STATIC_FILES = False

ADD_SCSS_FILES = [
    'rcportal/scss/nectar.scss',
    'rcportal/scss/bootstrap-toggle.scss',
]
