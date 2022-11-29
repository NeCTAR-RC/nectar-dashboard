# The name of the dashboard to be added to HORIZON['dashboards']. Required.
DASHBOARD = 'dashboard_home'

# If set to True, this dashboard will not be added to the settings.
DISABLED = False

# A list of applications to be added to INSTALLED_APPS.
ADD_INSTALLED_APPS = [
    'nectar_dashboard.dashboard_home',
    'nectar_dashboard.dashboard_home.welcome',
]

AUTO_DISCOVER_STATIC_FILES = True

ADD_SCSS_FILES = [
    'scss/slick-theme.scss',
    'scss/dashboard-home.scss',
]
