ADD_INSTALLED_APPS = [
    'rest_framework',
    'django_filters',
    'corsheaders',
    'select2',
]

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
    ('institutions',
     'nectar_dashboard.rcallocation.api.InstitutionViewSet', None),
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
     'nectar_dashboard.rcallocation.api.for.FORViewSet',
     'for-codes'),
    ('for-tree',
     'nectar_dashboard.rcallocation.api.for.AllocationTreeViewSet',
     'for-tree'),
)
