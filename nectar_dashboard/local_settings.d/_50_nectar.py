ADD_INSTALLED_APPS = [
    'rest_framework',
    'django_filters',
    'django_countries',
    'corsheaders',
    'select2',
    'mathfilters',
    'maintenance_mode'
]

MIDDLEWARE += ('maintenance_mode.middleware.MaintenanceModeMiddleware',)  # noqa
MAINTENANCE_MODE_STATE_BACKEND = "maintenance_mode.backends.CacheBackend"
MAINTENANCE_MODE_IGNORE_URLS = (r"^(?!/allocation.*$).*",)
MAINTENANCE_MODE_TEMPLATE = 'rcallocation/maintenance-mode.html'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# This is for rcshib, always use the configured keystone server
# as opposed to referrer.
WEBSSO_USE_HTTP_REFERER = False

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS':
    'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 1000,
    'DEFAULT_FILTER_BACKENDS':
    ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES':
    (
        'nectar_dashboard.rest_auth.CsrfExemptSessionAuthentication',
        'nectar_dashboard.rest_auth.KeystoneAuthentication',
    ),
}

REST_VIEW_SETS = (
    ('allocations',
     'nectar_dashboard.rcallocation.api.AllocationViewSet', None),
    ('quotas',
     'nectar_dashboard.rcallocation.api.QuotaViewSet', None),
    ('chiefinvestigators',
     'nectar_dashboard.rcallocation.api.ChiefInvestigatorViewSet', None),
    ('organisations',
     'nectar_dashboard.rcallocation.api.organisations.OrganisationViewSet',
     None),
    ('publications',
     'nectar_dashboard.rcallocation.api.PublicationViewSet', None),
    ('grants',
     'nectar_dashboard.rcallocation.api.GrantViewSet', None),
    ('resources',
     'nectar_dashboard.rcallocation.api.ResourceViewSet', None),
    ('zones',
     'nectar_dashboard.rcallocation.api.ZoneViewSet', None),
    ('service-types',
     'nectar_dashboard.rcallocation.api.ServiceTypeViewSet', None),
    ('ncris-facilities',
     'nectar_dashboard.rcallocation.api.NCRISFacilityViewSet', None),
    ('ardc-projects',
     'nectar_dashboard.rcallocation.api.ARDCSupportViewSet', None),
    ('sites',
     'nectar_dashboard.rcallocation.api.SiteViewSet', None),
    ('approvers',
     'nectar_dashboard.rcallocation.api.ApproverViewSet', None),
    ('for-codes',
     'nectar_dashboard.rcallocation.api.for.FOR2008ViewSet',
     'for-codes'),
    ('for-codes-2008',
     'nectar_dashboard.rcallocation.api.for.FOR2008ViewSet',
     'for-codes-2008'),
    ('for-codes-2020',
     'nectar_dashboard.rcallocation.api.for.FOR2020ViewSet',
     'for-codes-2020'),
    ('for-codes-all',
     'nectar_dashboard.rcallocation.api.for.FORAllViewSet',
     'for-codes-all'),
    ('for-tree',
     'nectar_dashboard.rcallocation.api.for.AllocationTree2008ViewSet',
     'for-tree'),
    ('for-tree-2008',
     'nectar_dashboard.rcallocation.api.for.AllocationTree2008ViewSet',
     'for-tree-2008'),
    ('for-tree-2020',
     'nectar_dashboard.rcallocation.api.for.AllocationTree2020ViewSet',
     'for-tree-2020'),
    ('for-tree-all',
     'nectar_dashboard.rcallocation.api.for.AllocationTreeAllViewSet',
     'for-tree-all'),
)
