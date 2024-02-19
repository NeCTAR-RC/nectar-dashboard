# The name of the dashboard to be added to HORIZON['dashboards']. Required.
DASHBOARD = 'allocation'

# If set to True, this dashboard will not be added to the settings.
DISABLED = False

# A list of applications to be added to INSTALLED_APPS.
ADD_INSTALLED_APPS = [
    'nectar_dashboard.rcallocation',
    'nectar_dashboard.rcallocation.allocation',
    'nectar_dashboard.rcallocation.allocation_approved',
    'nectar_dashboard.rcallocation.request',
    'nectar_dashboard.rcallocation.user_allocations',
]

AUTO_DISCOVER_STATIC_FILES = True

ADD_SCSS_FILES = [
    'rcportal/scss/nectar.scss',
    'rcportal/scss/bootstrap-toggle.scss',
    'rcportal/scss/bootstrap-select2.scss',
]
