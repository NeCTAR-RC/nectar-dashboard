import json
import logging

from django.core import exceptions

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import utils


LOG = logging.getLogger(__name__)


class Loader:
    def __init__(self):
        self.created = 0
        self.updated = 0
        self.disabled = 0

    def ror_record_to_org(self, ror):
        """Create or update an Organisation from a ROR record."""

        new = False
        ror_id = ror['id']
        enabled = ror['status'] == 'active'
        name = ror['name']
        country = ror['country']['country_code'].upper()
        if ror['acronyms']:
            short = ror['acronyms'][0]
        elif ror['aliases']:
            short = ror['aliases'][0]
        else:
            short = ""
        if len(short) > 16:
            short = ""
        org = None
        try:
            org = models.Organisation.objects.get(ror_id=ror_id)
            if org.enabled and not enabled:
                self.disabled += 1
            org.full_name = name
            org.short_name = short
            org.enabled = enabled
            org.country = country
            org.save()
            self.updated += 1
        except exceptions.ObjectDoesNotExist:
            self.created += 1
            org = models.Organisation.objects.create(
                ror_id=ror_id,
                enabled=enabled,
                full_name=name,
                short_name=short,
                country=country,
            )
            new = True
        return (org, new)

    def load(self, uri, initial=False):
        parents = {}
        predecessors = {}
        with utils.open_config_file(uri) as fp:
            LOG.info(f"Loading ROR dump JSON from {uri}")
            ror_data = json.load(fp)
            LOG.info(f"Loaded {len(ror_data)} JSON records")
            LOG.info("Creating / updating DB records")
            for ror in ror_data:
                (org, new) = self.ror_record_to_org(ror)

                # Collect the relationships for a second pass
                if org and org.enabled:
                    if 'relationships' in ror:
                        for rel in ror['relationships']:
                            if rel['type'] == 'Parent':
                                parents[org.ror_id] = rel['id']
                            elif rel['type'] == 'Predecessor':
                                if org.ror_id in predecessors:
                                    predecessors[org.ror_id].append(rel['id'])
                                else:
                                    predecessors[org.ror_id] = [rel['id']]
                if (self.created + self.updated) % 10000 == 0:
                    LOG.info(f'progress: {self.created}, {self.updated}')

            if not initial:
                LOG.info("Clearing stale relationships")
                # We need to clear all relationships between orgs in the
                # ROR, but retain any relationships that involve non-ROR
                # orgs ... on either side of the relationship
                for o in (
                    models.Organisation.objects.exclude(ror_id='')
                    .exclude(parent=None, precedes=None)
                    .prefetch_related('parent', 'precedes')
                ):
                    touched = False
                    if o.parent and o.parent.ror_id:
                        o.parent = None
                        touched = True
                    for p in o.precedes.all():
                        if p.ror_id:
                            o.precedes.remove(p)
                            touched = True
                    if touched:
                        o.save()

            LOG.info("Adding parent relationships")
            count = 0
            for c, p in parents.items():
                child = models.Organisation.objects.get(ror_id=c)
                parent = models.Organisation.objects.get(ror_id=p)
                child.parent = parent
                child.save()
                count += 1
            LOG.info(f"Added {count} parent relationships")

            LOG.info("Adding predecessor relationships")
            # Note that there are no Successor / Predecessor relationships
            # in early ROR dumps; e.g. v1.8.  So don't be alarmed ...
            count = 0
            for s, pl in predecessors.items():
                successor = models.Organisation.objects.get(ror_id=s)
                for p in pl:
                    predecessor = models.Organisation.objects.get(ror_id=p)
                    successor.supersedes.add(predecessor)
                    count += 1
                successor.save()
            LOG.info(f"Added {count} predecessor relationships")

            LOG.info(
                f"Added {self.created} and refreshed "
                f"{self.updated} organisations"
            )
            if self.disabled:
                LOG.info(
                    f"{self.disabled} of the existing organisations "
                    "were disabled"
                )
