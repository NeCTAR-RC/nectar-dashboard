# The name of the dashboard to be added to HORIZON['dashboards']. Required.
DASHBOARD = 'allocation'

# If set to True, this dashboard will not be added to the settings.
DISABLED = False

# A list of applications to be added to INSTALLED_APPS.
ADD_INSTALLED_APPS = [
    'nectar_dashboard.rcallocation.crams',
]

AUTO_DISCOVER_STATIC_FILES = True

ADD_SCSS_FILES = [
    'rcportal/scss/jquery.mDialog.scss',
    'rcportal/scss/nectar.scss',
]
