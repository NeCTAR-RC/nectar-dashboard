from nectar_dashboard.rcallocation import models


class Catalog(object):

    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)


def make_migration_catalog(apps):
    def _get_model(name):
        try:
            return apps.get_model('rcallocation', name)
        except LookupError:
            return None

    return Catalog(ORG_ALL_SHORT_NAME=models.ORG_ALL_SHORT_NAME,
                   ORG_ALL_FULL_NAME=models.ORG_ALL_FULL_NAME,
                   ORG_UNKNOWN_SHORT_NAME=models.ORG_UNKNOWN_SHORT_NAME,
                   ORG_UNKNOWN_FULL_NAME=models.ORG_UNKNOWN_FULL_NAME,
                   AllocationRequest=_get_model('AllocationRequest'),
                   Organisation=_get_model('Organisation'),
                   Institution=_get_model('Institution'),
                   ChiefInvestigator=_get_model('ChiefInvestigator'),
                   Approver=_get_model('Approver'))
