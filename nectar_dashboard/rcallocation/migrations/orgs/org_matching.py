import json
import logging
import re

from django.core import exceptions

from nectar_dashboard.rcallocation import utils


LOG = logging.getLogger(__name__)


def backfill(catalog, strict=True):
    # Deal with legacy and other allocations where no supported
    # organisations have been set
    LOG.info("Fixing allocations with no supported organisation")
    unknown_org = catalog.Organisation.objects.get(
        full_name=catalog.ORG_UNKNOWN_FULL_NAME)
    count = 0
    errors = 0
    for a in catalog.AllocationRequest.objects.filter(
            supported_organisations=None):
        if strict \
           and catalog.Institution.objects.filter(allocation=a).count() > 0:
            # These need to be investigated!
            qual = f"(parent {a.parent_request.id})" if a.parent_request \
                else ""
            LOG.info(f"Allocation {a.id} {qual} has institutions but "
                     f"no supported orgs")
            errors += 1
        else:
            # Backfill with "unknown"
            count += 1
            a.supported_organisations.add(unknown_org)
            utils.save_allocation_without_updating_timestamps(a)

    if count:
        LOG.info(f"Fixes {count} allocation records")

    LOG.info("Scanning for CIs with no primary organisation")
    for ci in catalog.ChiefInvestigator.objects \
                                       .filter(primary_organisation=None):
        if strict:
            errors += 1
            # These need to be investigated!
            if ci.institution.strip():
                LOG.info(f"CI for allocation {ci.allocation.id} has no "
                     "institution")
            else:
                LOG.info(f"CI for allocation {ci.allocation.id} has no "
                         f"org (institution is '{ci.institution}')")
        else:
            ci.primary_organisation = unknown_org
            ci.save()

    if errors:
        raise Exception(f"{errors} Allocations or CIs require "
                        "further investigation")


class LocalOrganisationMappings(object):
    """All of the local data related to the migration.  Misspellings,
    mappings for organisations recorded with irregular names, crap filtering
    and registrations for local organisations that are not in the ROR ...
    but could / should be.
    """

    # Variant (incorrect) spellings.  The zero'th element of each list
    # is the correct spelling.  These corrections will be applied before
    # any matching is done.
    spelling = [
        ['university', 'univerity', 'unoversity', 'universitty',
         'universitry', 'univesrity', 'univversity', 'unversity',
         'unviersity', 'univerisity', 'univeristy', 'universty',
         'universtiy', 'universities', 'universitu', 'universoty',
         'univesity', 'univerisy', 'uni', 'u', 'univ'],
        ['australian', 'australlian', 'austrlian'],
        ['aapp', 'aaap'],
        ['australia', 'australi', 'australiaå'],
        ['newcastle', 'newcasstle'],
        ['southern', 'souther'],
        ['monash', 'monahs', 'moansh'],
        ['intersect', 'intersec'],
        ['csiro', 'ciro'],
        ['institute', 'institue', 'institude'],
        ['melbourne', 'melrbourne', 'melborne', 'melnourne', 'melbournei',
         'melbourme', 'melblourne', 'melbourrne', 'melbroune', 'mebourne',
         'fmelbourne', 'melbounre', 'melboune'],
        ['auckland', 'acukland', 'auckalnd', 'aucland', 'aukcland'],
        ['murdoch', 'murdoc'],
        ['macquarie', 'macuqarie'],
        ['technology', 'rechnology', 'techology', 'technololgy'],
        ['tasmania', 'tamania', 'tasmaniaa', 'tasmani', 'tasmaina'],
        ['queensland', 'queenlsand', 'qld', 'queenland', 'queenssland',
         'queesnland'],
        ['western', 'wstern'],
        ['sydney', 'sysney', 'syd'],
        ['cquniversity', 'cquni', 'cqu', 'cquniveristy'],
        ['swinburne', 'siwnburne', 'swinburnew'],
        ['dst', 'dsto', 'dstg'],
        ['cancer', 'caner'],
        ['princess', 'prince'],
        ['alexandra', 'alexandria'],
        ['pennsylvania', 'penn'],
        ['indigenous', 'idigenous'],
        ['meteorology', 'meterorology']
    ]

    s_map = {s[i]: s[0] for s in spelling for i in range(1, len(s))}

    # Words to ignore when doing heuristic matching
    noise = ['the', 'te', 'tthe', 'thee',
             'of', 'od', 'o',
             'for', ',', 'initially']

    def __init__(self, catalog):
        self.catalog = catalog

    # A grab bag of special case mappings.
    def fixup(self, text):       # noqa : C901        
        """Takes a text string that matched by other methods and attempts
        to map it to a known organisation.  The result will be an
        organisation ROR id or names.  Or a list of them.  Or "unknown" or
        "all".  If None is returned, we have something that needs attention.
        """

        ALL = self.catalog.ORG_ALL_SHORT_NAME
        UNKNOWN = self.catalog.ORG_UNKNOWN_SHORT_NAME

        # Start by splitting out
        text = text.lower()
        split = re.split(r'\W+', text)
        words = [s for s in split if s not in self.noise]

        # This one is a real mess ...
        if text.startswith('acrf'):
            return [self.name_map["Centre for Cancer Biology"],
                    self.name_map["Australian Cancer Research Foundation"]]

        # General crap filters
        if text == "'all'" or words[0] == 'all' or 'various' in words \
           or 'various' in words or 'worldwide' in words \
           or 'multiple' in words \
           or 'numerous' in words or 'subscribers' in words \
           or 'community' in words or 'go8' in words \
           or 'collaborating' in words:
            return ALL
        elif text in ['test', 'testing', 'na', 'n/a', 'fnoord',
                      'please delete', 'vvvv', 'zzzz', 'blarg',
                      'ssss', 'yoyo', 'yoyo.com', 'example.org']:
            return UNKNOWN
        elif text.startswith('http:') or text.startswith('https:'):
            return UNKNOWN
        elif text.startswith('but all'):
            return UNKNOWN
        elif 'in' in words and 'talks' in words:
            return UNKNOWN
        elif 'ands' in words or 'nectar' in words or 'rds' in words \
             or 'ardc' in words:
            return self.name_map['Australian Research Data Commons']
        elif text == 'australian national data service':
            return self.name_map['Australian Research Data Commons']
        elif 'aarnet' in words:
            return self.name_map['AARNet (Australia)']
        elif 'qimr' in words:
            return self.name_map["QIMR Berghofer Medical Research Institute"]
        elif 'uq' in words or 'qaaf' in words or 'qaafi' in words \
             or 'rcc' in words or 'uoq' in words or 'diamantina' in words \
             or 'cmm' in words or 'poche' in words \
             or ('research' in words and 'computing' in words
                 and 'centre' in words
             ) or 'advanced' in words and 'imaging' in words \
             or 'global' in words and 'change' in words \
             or ('institute' in words and 'bioengineering' in words
                 and 'nanotechnology' in words
             ) or 'institute' in words and 'molecular' in words \
             or 'institute' in words and 'brain' in words:
            return self.name_map["University of Queensland"]
        elif 'monash' in words or 'caulfield' in words \
             or 'turner' in words or 'ltrac' in words:
            return self.name_map["Monash University"]
        elif 'jcu' in words or 'james' in words and 'cook' in words \
             or 'tropwater' in words:
            return self.name_map["James Cook University"]
        elif 'griffith' in words or 'glycomics' in words or "gu" in words \
             or 'international' in words and 'water' in words \
             or 'suicide' in words and 'prevention' in words:
            return self.name_map["Griffith University"]
        elif 'cquniversity' in words or 'ucq' in words:
            return self.name_map["Central Queensland University"]
        elif 'unisc' in words:
            return self.name_map["University of the Sunshine Coast"]
        elif 'anu' in words:
            return self.name_map["Australian National University"]
        elif 'uwa' in words or 'university' in words and 'wa' in words:
            return self.name_map["University of Western Australia"]
        elif 'deakin' in words:
            return self.name_map["Deakin University"]
        elif 'curtin' in words:
            return self.name_map["Curtin University"]
        elif 'macquarie' in words:
            return self.name_map["Macquarie University"]
        elif 'swinburne' in words:
            return self.name_map["Swinburne University of Technology"]
        elif 'auckland' in words or 'liggins' in words \
             or 'compass' in words or 'augmented' in words or 'isom' in words:
            return self.name_map["University of Auckland"]
        elif 'usq' in words:
            return self.name_map["University of Southern Queensland"]
        elif 'latrobe' in words or 'la' in words and 'trobe' in words:
            return self.name_map["La Trobe University"]
        elif 'flinders' in words or 'flindersuniversity' in words:
            return self.name_map["Flinders University"]
        elif text == 'q.u.t.' or text == "queensland university of queensland":
            return self.name_map["Queensland University of Technology"]
        elif 'unsw' in words or 'nsw' in words and 'university' in words \
             or 'astrobiology' in words:
            return self.name_map["UNSW Sydney"]
        elif 'nsw' in words and ('dpi' in words or 'primary' in words):
            return self.name_map[
                "New South Wales Department of Primary Industries"]
        elif text == 'nsw gov':
            return self.name_map["Government of New South Wales"]
        elif 'uows' in words or 'wsu' in words or 'marcs' in words \
             or 'uo' in words and 'western' in words and 'sydney' in words:
            return self.name_map["Western Sydney University"]
        elif 'federation' in words:
            return self.name_map["Federation University"]
        elif 'jumbunna' in words:
            return self.name_map["University of Technology Sydney"]
        elif 'charles' in words and 'perkins' in words \
             or text == 'uos':
            return self.name_map["University of Sydney"]
        elif 'australian' in words and 'antarctic' in words \
             and 'division' in words:
            return self.name_map["Australian Antarctic Division"]
        elif 'imas' in words or 'tasmania' in words and 'library' in words \
             or text == 'sense-t' \
             or text == 'project professor':
            return self.name_map["University of Tasmania"]
        elif 'aodn' in words:
            return self.name_map["Integrated Marine Observing System"]
        elif 'ga' in words:
            return self.name_map["Geoscience Australia"]
        elif 'royal' in words and 'melbourne' in words:
            return self.name_map["RMIT University"]
        elif 'melbourne' in words or 'uom' in words \
             or 'melb' in words or 'unimelb' in words or 'melbuni' in words \
             or 'cdmps' in words or 'csdila' in words \
             or 'mnsi' in words or 'cebra' in words or 'bio21' in words \
             or 'centre' in words and 'palliative' in words \
             or 'centre' in words and 'disaster' in words \
             or 'networked' in words and 'society' in words \
             or 'spatial' in words and 'data' in words and 'land' in words:
            return self.name_map["University of Melbourne"]
        elif 'florey' in words:
            return self.alias_map["Florey Institute"]
        elif 'doherty' in words:
            return self.name_map["Peter Doherty Institute"]
        elif 'nvidia' in words:
            return self.name_map['Nvidia (United States)']
        elif 'data61' in words or ('data' in words and '61' in words):
            return self.name_map['Data61']
        elif 'csiro' in words:
            return self.name_map['Commonwealth Scientific and Industrial '
                            'Research Organisation']
        elif text == 'qld gov':
            return self.name_map['Queensland Government']
        elif 'pawsey' in words:
            return self.name_map["Pawsey Supercomputing Research Centre"]
        elif 'intersect' in words:
            return self.name_map["Intersect"]
        elif 'nci' in words:
            return self.name_map["National Computational Infrastructure"]
        elif 'terrestrial' in words or 'ozflux' in words:
            return self.acronym_map["TERN"]
        elif 'murdoch' in words:
            return self.name_map["Murdoch Children's Research Institute"]
        elif 'olivia' in words:
            return self.name_map["Olivia Newton-John Cancer Wellness & "
                            "Research Centre"]
        elif 'hall' in words:
            return self.alias_map["Walter and Eliza Hall Institute"]
        elif 'children' in words and 'cancer' in words:
            return self.name_map["Children's Cancer Institute Australia"]
        elif 'garvan' in words:
            return self.name_map["Garvan Institute of Medical Research"]
        elif 'ingham' in words:
            return self.name_map["Ingham Institute"]
        elif 'wicking' in words or 'menzies' in words:
            return self.name_map["University of Tasmania"]
        elif 'aceas' in words or 'antarctic' in words or 'aims' in words \
             or 'ace' in words or 'acecrc' in words:
            return self.name_map["University of Tasmania"]
        elif 'woodside' in words:
            return self.name_map["Woodside (Australia)"]
        elif 'liverpool' in words:
            return self.name_map["Liverpool Hospital"]
        elif 'parc' in words:
            return self.name_map["Palo Alto Research Center"]
        elif 'tpac' in words \
             or "tasmanian" in words and "partnership" in words:
            return self.reg_map['tpac']
        elif 'sa' in words and 'museum' in words:
            return self.name_map["South Australian Museum"]
        elif text == 'sa gov':
            return self.name_map["Government of South Australia"]
        elif 'nea' in words:
            return self.name_map["National Environment Agency"]
        elif 'epworth' in words:
            return self.name_map["Epworth Hospital"]
        elif 'peter' in words or 'petermac' in words or 'pmcc' in words:
            return self.name_map["Peter MacCallum Cancer Centre"]
        elif 'hokkaido' in words:
            return self.name_map["Hokkaido University"]
        elif 'sanger' in words:
            return self.name_map["Wellcome Sanger Institute"]
        elif 'tropical' in words and 'biocommodities' in words:
            return self.name_map["Queensland University of Technology"]
        elif 'co2crc' in words:
            return self.alias_map["Cooperative Research Centre for Greenhouse "
                                  "Gas Technologies"]
        elif 'agrf' in words:
            return self.name_map["Australian Genome Research Facility"]
        elif 'sydney' in words and 'marine' in words:
            return self.name_map["Sydney Institute of Marine Science"]
        elif 'australian' in words and 'marine' in words:
            return self.name_map["Australian Institute of Marine Science"]
        elif 'national' in words and 'computing' in words:
            return self.name_map["National Computational Infrastructure"]
        elif 'iatsis' in words:
            return self.name_map["Australian Institute of Aboriginal and "
                            "Torres Strait Islander Studies"]
        elif 'cotton' in words:
            return self.name_map["Cotton Research and Development Corporation"]
        elif 'terascale' in words:
            return self.name_map["ARC Centre of Excellence for Particle "
                                 "Physics at the Terascale"]
        elif 'infrastructure' in words and 'engineering' in words \
             or 'hie' in words or 'scem' in words:
            return self.name_map["Western Sydney University"]
        elif 'africarice' in words:
            return self.name_map["Africa Rice Center"]
        elif 'arc' in words:
            return self.name_map["Australian Research Council"]
        elif 'acad' in words or 'robinson' in words \
             or text == "australian institute for machine learning":
            return self.name_map["University of Adelaide"]
        elif 'nt' in words and 'gov' in words:
            return self.name_map["Government of the Northern Territory"]
        elif 'nt' in words and 'dpi' in words:
            return self.name_map[
                "Department of Primary Industry and Resources"]
        elif 'idigenous' in words:
            return self.name_map["University of Southern Queensland"]
        elif 'new' in words and 'castle' in words:
            return self.name_map["University of Newcastle Australia"]
        elif 'okinawa' in words:
            return self.name_map[
                "Okinawa Institute of Science and Technology "
                "Graduate University"]
        elif 'pasteur' in words:
            return self.name_map["Institut Pasteur"]
        elif 'merc' in words:
            return self.name_map["Monash University"]
        elif 'cern' in words:
            return self.name_map["European Organization for Nuclear Research"]
        elif 'bird' in words and 'life' in words:
            return self.name_map["BirdLife Australia"]
        elif 'ilmenau' in words:
            return self.name_map["Technische Universität Ilmenau"]
        elif 'collecte' in words:
            return self.name_map["Collecte Localisation Satellites (France)"]
        elif 'sugar' in words:
            return self.name_map["Sugar Research Australia (Australia)"]
        elif 'lbnl' in words:
            return self.name_map["Lawrence Berkeley National Laboratory"]
        elif 'graham' in words:
            return self.name_map["Charles Sturt University"]
        elif 'noaa' in words:
            return self.name_map[
                "National Oceanic and Atmospheric Administration"]
        elif 'feit' in words:
            return self.name_map["University of Technology Sydney"]
        elif 'odi' in words:
            return self.name_map["Open Data Institute"]
        elif 'nhmrc' in words and 'clinical' in words:
            return self.name_map["University of Sydney"]
        elif 'northwest' in words:
            return self.name_map[
                "North West Agriculture and Forestry University"]
        elif text == 'vic gov':
            return self.name_map["Government of Victoria"]
        elif 'berman' in words:
            return self.name_map[
                "Berman Center for Outcomes and Clinical Research"]
        elif 'westlake' in words:
            return self.name_map["Westlake University"]
        elif 'sunway' in words:
            return self.name_map["Sunway University"]
        elif 'nih' in words:
            return self.name_map["National Institutes of Health"]
        elif 'tgac' in words:
            return self.name_map["Earlham Institute"]
        elif 'joint' in words and 'commission' in words:
            # This is ambiguous.  There are 5 child organisations of vvv
            # in different locations all called "Joint Research Centre".
            # (I thought the names were supposed to be unique ...)
            return self.name_map["Directorate-General Joint Research Centre"]
        elif 'plant' in words and 'energy' in words:
            return self.name_map[
                "ARC Centre of Excellence in Plant Energy Biology"]
        elif 'gairdner' in words:
            return self.name_map["Sir Charles Gairdner Hospital"]
        elif 'uconn' in words:
            return self.name_map["University of Connecticut"]
        elif 'ucsb' in words:
            return self.name_map["University of California, Santa Barbara"]
        elif 'massachusetts' in words:
            return self.name_map["University of Massachusetts Amherst"]
        elif 'wa' in words and 'gov' in words:
            return self.name_map["Government of Western Australia"]
        elif 'indigenous' in words and 'genomics' in words:
            return self.name_map["Australian National University"]
        elif 'san' in words and 'antonio' in words:
            return self.name_map["The University of Texas Health Science "
                            "Center at San Antonio"]
        elif 'texas' in words:
            return [
                self.name_map["The University of Texas Southwestern "
                         "Medical Center"],
                self.name_map["The University of Texas Medical Branch "
                         "at Galveston"]]
        elif 'us' in words and 'air' in words:
            # Close enough ...
            return self.name_map["United States Air Force Research Laboratory"]
        elif 'mānoa' in words:
            return self.name_map["University of Hawaii at Manoa"]
        elif 'dedjtr' in words:
            return self.name_map["Department of Economic Development "
                            "Jobs Transport and Resources"]
        elif 'manukau' in words:
            return self.name_map["Counties Manukau District Health Board"]
        elif 'waitematā' in words:
            return self.name_map["Waitemata District Health Board"]
        elif 'karolinska' in words:
            # "Karolinska Institute" / "Karolinska Institutet" - the
            # ROR primary name changes between v1.8 and v1.20
            return "https://ror.org/056d84691"
        elif 'embl' in words and 'australia' in words:
            return self.name_map["EMBL Australia"]

        # Full text matches
        if text == 'vlsci':
            # Newer than my data dump ...
            return "https://ror.org/05gkzhv48"
        elif text == 'western public health unit':
            return self.name_map["Western Health"]
        elif text == 'western australia health' \
             or 'wa' in words and 'health' in words:
            return self.name_map["Government of Western Australia "
                            "Department of Health"]
        elif text == 'wa daf' \
             or text == 'wa department of water':
            return self.name_map["Department of Agriculture and Food "
                            "Western Australia"]
        elif text == 'environmental science and research, nz':
            return self.name_map[
                "Institute of Environmental Science and Research"]
        elif text == 'dpi':
            return self.name_map[
                "New South Wales Department of Primary Industries"]
        elif text == 'eresearch' \
             or text == "biomedicine discovery institute" \
             or text == "australian centre for blood diseases" \
             or text == "department of econometrics and business statistics" \
             or text == "biological science":
            return self.name_map["Monash University"]
        elif text == "australian infectious disease research centre" \
             or text == "institute for teaching and learning innovation" \
             or text == "institute for social science research" \
             or text == "frazer institute":
            return self.name_map["University of Queensland"]
        elif text == '(australian public)' or text == 'public':
            return ALL
        elif text == 'centre for eresearch' \
             or text == 'business school' \
             or text == 'computer science' \
             or text == 'plant and food research' \
             or text == 'photon factory' \
             or text == 'faculty of medical and health sciences' \
             or text == 'molecular medicine and pathology':
            return self.name_map["University of Auckland"]
        elif text == 'civil and mechanical department':
            return self.name_map["Curtin University"]
        elif text == 'data.gov.au':
            return self.name_map["Australian Government"]
        elif text == 'data.qld.gov.au':
            return self.name_map["Queensland Government"]
        elif text == 'deaprtment of human services':
            return self.name_map['Services Australia']
        elif text == "a*star singapore":
            return self.name_map["Agency for Science, Technology and Research"]
        elif text == 'western australia school of mines':
            return self.name_map["Curtin University"]
        elif text == "national centre for australian children's literature":
            return self.name_map["University of Canberra"]
        elif text == 'national center for maritime engineering ' \
             'and hydrodynamics':
            return self.name_map["Australian Maritime College"]
        elif text == 'institute for culture and society':
            return self.name_map["Western Sydney University"]
        elif text == 'qld dnrm' or text == 'qld dnrme' \
             or text == 'qld department of natural resources, mines & energy':
            return self.name_map['Department of Natural Resources, Mines '
                            'and Energy']
        elif text == 'uk institute for cancer research, sutton, surrey uk':
            # The map doesn't work.  "Institute of Cancer Research" is
            # ambiguous.
            return "https://ror.org/043jzw605"
        elif text == 'queensland department of the environment' \
             or text == 'department of environment and heritage protection':
            return self.name_map[
                'Queensland Department of Environment and Science']
        elif text == 'queensland department of the environment':
            return self.name_map[
                'Queensland Department of Environment and Science']
        elif text == 'queensland goverment (department of environment and ' \
             'sciences and department of natural resources and mines)':
            return [self.name_map['Queensland Department of Environment '
                             'and Science'],
                    self.name_map['Department of Natural Resources, '
                             'Mines and Energy']]
        elif text == 'nsw office of environment and heritage':
            return self.name_map['NSW Department of Planning, Industry '
                            'and Environment']
        elif text == 'defence science and technology':
            return self.name_map['Defence Science and Technology Group']

        # Unregistered stuff
        if 'dsiti' in words and 'oeh' in words:
            return [
                self.name_map['NSW Department of Planning, Industry '
                         'and Environment'],
                self.reg_map['dsiti']]
        elif 'natag' in words \
             or 'fed' in words and 'govt' in words and 'energy' in words:
            return self.reg_map['dcceew']
        elif text == 'qld daf' \
             or text == 'qld dept. of ag, and fish' \
             or text == 'queensland department of agriculture and fisheries':
            return self.reg_map['qdaf']
        elif text == 'qld dsiti' \
             or text == 'queensland government department of science, ' \
             'information technology and innovation':
            return self.reg_map['dsiti']
        elif text == 'qld':
            return self.reg_map['rdmw']
        elif text == 'pathology queensland':
            return self.reg_map['pq']
        elif text == 'public record office victoria':
            return self.reg_map['prov']
        elif 'ersa' in words or 'eresearch' in words and 'sa' in words:
            return self.reg_map['ersa']
        elif 'qfab' in words \
             or text == 'queensland facility of bioinformatics':
            return self.reg_map['qfab']
        elif 'qcif' in words:
            return self.reg_map['qcif']
        elif 'water' in words and 'cities' in words:
            return self.reg_map['crcwsc']
        elif 'bioplatforms' in words or 'biocommons' in words:
            return self.reg_map['bioplatforms']
        elif 'aussrc' in words:
            return self.reg_map['aussrc']
        elif 'cyber' in words:
            return self.reg_map['cscrc']
        elif 'imove' in words:
            return self.reg_map['imove']
        elif 'soil' in words or 'soils' in words:
            return self.reg_map['soil']
        elif 'algorand' in words:
            return self.reg_map['algorand']
        elif 'agilent' in words:
            return self.reg_map['agilent']
        elif 'd2d' in words or 'decisions' in words and 'crc' in words:
            return self.reg_map["d2dcrc"]
        elif 'clex' in words:
            return self.reg_map["climateextremes"]
        elif 'aapp' in words:
            return self.reg_map['aapp']
        elif 'fornier' in words:
            return self.reg_map['frontiersi']
        elif 'agp' in words:
            return self.reg_map['agp']
        elif 'health' in words and 'outcome' in words and 'nz' in words:
            return self.reg_map['chomnz']
        elif 'dynamics' in words and 'language' in words:
            return self.reg_map['coedl']
        elif 'agrifutures' in words:
            return self.reg_map['agrifutures']
        elif 'inova' in words and 'schar' in words:
            return self.reg_map['inovaschar']
        elif 'njernda' in words:
            return self.reg_map['njernda']
        elif 'australia' in words and 'indonesia' in words:
            return self.reg_map['aic']
        elif 'act' in words and 'gov' in words:
            return self.reg_map['act']
        elif 'tas' in words and 'gov' in words:
            return self.reg_map['tas']
        elif text == 'tasmanian government department of primary ' \
             'industries, parks, water and environment' \
             or text == 'department or primary ondustries, parks, water ' \
             'and environment':
            return self.reg_map['dpipwe']
        elif text == 'department of natural resources and ' \
             'environment tasmania' \
             or text == 'tasmanian government department of natural ' \
             'resources and environment':
            return self.reg_map['nre']
        elif text == 'department or primary industries, parks, water ' \
             'and environment':
            return self.reg_map['dpipwe']
        elif 'rumbalara' in words:
            return self.reg_map['rumbalara']
        elif 'echuca' in words:
            return self.reg_map['erh']
        elif 'campaspe' in words:
            return self.reg_map['campaspe']
        elif 'veterinary' in words:
            return self.reg_map['anzcvs']
        elif 'herbarium' in words or 'royal' in words and 'botanic' in words:
            return self.reg_map['rbg']
        elif 'netcare' in words:
            return self.reg_map['netcare']
        elif text == 'first languages australia':
            return self.reg_map['firstlanguages']
        elif text == 'australian rainforest conservation society':
            return self.reg_map['arcs']
        elif text == 'forests alive':
            return self.reg_map['forestsalive']
        elif text == 'australian prostate cancer research centre':
            return self.reg_map['apcrc-q']
        elif text == 'invertebrates australia':
            return self.reg_map['invertebratesau']
        elif text == 'land solution australia':
            return self.reg_map['landsolution']
        elif text == 'cancer crc':
            return self.reg_map['ctx']
        elif text == 'forest practices authority (fpa)':
            return self.reg_map['fpa']
        elif text == 'qvmag':
            return self.reg_map['qvmag']
        elif text == 'royal childrens hospital':
            return self.reg_map['rch']
        elif text == 'sustainable timber tasmania (stt)':
            return self.reg_map['stt']
        elif text == 'national association of diabetes centres':
            return self.reg_map['nadc']
        elif text == 'digital transformation agency':
            return self.reg_map['dta']
        elif 'metabalomics' in words:
            return [
                self.reg_map['ma'],
                self.name_map["University of Melbourne"]]
        elif 'phoenix' in words:
            return self.reg_map['phoenix']
        elif 'shepparton' in words:
            return self.reg_map['shepparton']
        elif '2030' in words:
            return self.reg_map['race']
        elif 'hazards' in words:
            return self.reg_map['naturalhazards']
        elif 'vietnam' in words:
            return self.reg_map['nghv']
        elif 'southern' in words and 'ocean' in words:
            return self.reg_map['soos']
        elif 'burnett' in words:
            return self.reg_map['burnett']
        elif 'nrm' in words:
            return self.reg_map['nrmsouth']
        elif 'tmag' in words:
            return self.reg_map['tmag']
        elif 'vicforests' in words:
            return self.reg_map['vicforests']
        elif 'vicnode' in words:
            return self.reg_map['vicnode']
        elif 'afac' in words:
            return self.reg_map['afac']

        # Really stupid stuff ...
        if 'sinai' in words:
            # Probably a Mt Sinai hospital in USA, but there are many and
            # the context doesn't allow disambiguation
            return UNKNOWN
        elif '@' not in text and ('au' in words or 'mu') in words:
            # Ambiguous (non-standard) university acronyms
            return UNKNOWN
        elif text == 'a;;':
            return self.reg_map["qcif"]
        elif 'mrudhula' in words \
             or text == 'faculty of science, engineering & technology':
            return self.name_map["Swinburne University of Technology"]
        elif 'supervisor' in words \
             or text == 'school of medicine' \
             or text == 'school of biomedical sciences' \
             or text == 'school of biological sciences' \
             or text == 'school of agriculture and food science' \
             or text == 'school of chemistry and molecular biosciences' \
             or text == 'school of civil engineering' \
             or 'institue' in words and 'queensland' in words:
            return self.name_map["University of Queensland"]
        elif text == "au":
            return self.name_map["University of Adelaide"]
        elif text == "an.zhao@unisa.edu.au" or text == "usa":
            return self.name_map["University of South Australia"]
        elif text == "petra.heil@utas.edu.au" or text == "tasmania":
            return self.name_map["University of Tasmania"]
        elif text == "university and local cultural institutions":
            # What institutions?
            return self.name_map["University of Tasmania"]
        elif text == "nitin.mantri@rmit.edu.au":
            return self.name_map["RMIT University"]
        elif text == "cap  des team":
            return self.name_map["Australian National University"]
        elif text == 'distributedcomputing' \
             or text == 'distributed computing' \
             or text == 'information system' \
             or text == 'information and technology faculty' \
             or text == 'science it, faculty of science' \
             or text == 'engineering and it' \
             or text == 'school of biosciences' \
             or text == 'school of computing and information systems' \
             or text == 'school of ecosystem and forest sciences' \
             or text == ("we are working nationally with archives "
                         "in wa, sa, act and nt"
             ) or 'director' in words \
             or 'riyad' in words and 'hossen' in words \
             or 'clouds' in words and 'lab' in words \
             or 'school' in words and 'engineer' in words \
             or 'box' in words and '3523' in words:
            return self.name_map["University of Melbourne"]
        elif text == "research school of finance, actuarial studies " \
             "and statistics, college of business and economics":
            return self.name_map["Australian National University"]
        elif text == "civil and mechanical engineering department":
            return self.name_map["Curtin University"]
        elif text == "faculty of science":
            return self.name_map["Monash University"]
        elif text == "external collaborators":
            return UNKNOWN
        elif text == "faculty of medicine":
            # Ambiguous: same text mean different things in 2 different
            # allocations
            return [
                {'parent_id': 30611,
                 'ror': self.name_map["University of Queensland"]
                },
                {'parent_id': 82733,
                 'ror': self.name_map["Monash University"]
                }
            ]
        else:
            return None

    def registrations(self):
        # Cheat ... IMAS is not an independent organisation but we have
        # a few examples that are partial matches
        self.acronym_map['imas'] = self.name_map['University of Tasmania']

        self.register(self.catalog.ORG_ALL_SHORT_NAME,
                      self.catalog.ORG_ALL_FULL_NAME)
        self.register(self.catalog.ORG_UNKNOWN_SHORT_NAME,
                      self.catalog.ORG_UNKNOWN_FULL_NAME,
                      enabled=False)
        self.register('dsiti', 'Queensland Department of Science, Information '
                      'Technology and Innovation',
                      successor=self.name_map[
                          'Queensland Department of Environment and Science'],
                      parent=self.name_map['Queensland Government'])
        self.register('dcceew', 'Department of Climate Change, Energy, the '
                      'Environment and Water',
                      parent=self.name_map['Australian Government'])
        self.register('qdaf',
                      'Queensland Department of Agriculture and Fisheries',
                      parent=self.name_map['Queensland Government'])
        self.register('rdmw',
                      'Department of Regional Development, Manufacturing '
                      'and Water',
                      parent=self.name_map['Queensland Government'])
        self.register('PQ', 'Pathology Queensland',
                      url='https://www.health.qld.gov.au/'
                      'public-health/pathology-queensland',
                      parent=self.name_map["Queensland Health"])
        self.register('prov', 'Public Record Office Victoria',   # sic!
                      url='https://prov.vic.gov.au',
                      parent=self.name_map['Government of Victoria'])
        self.register('eRSA', "eResearch South Australia",
                      url='https://ersa.edu.au', enabled=False)
        self.register('QCIF', "Queensland Cyber Infrastructure Foundation",
                      url='https://qcif.edu.au',
                      ror=' https://ror.org/03sd43014')
        self.register('QFAB', "Queensland Facility for Applied Bioinformatics",
                      url='https://qfab.org',
                      successor=self.reg_map['qcif'])
        self.register('CRCWSC', 'CRC for Water Sensitive Cities',
                      url='https://watersensitivecities.org.au')
        self.register('BioPlatforms', 'BioPlatforms Australia',
                      url='https://bioplatforms.com')
        self.register('AusSRC', 'Australian SKA Regional Centre',
                      url='https://aussrc.org')
        self.register('CSCRC', 'Cyber Security CRC',
                      url='https://cybersecuritycrc.org.au', enabled=False)
        self.register('iMOVE', 'iMOVE Australia',
                      url='https://imoveaustralia.com')
        self.register('SOIL', 'CRC for High Performance Soils',
                      url='https://soilcrc.com.au')
        self.register('Algorand', 'Algorand Inc',
                      url='https://www.algorand.com',
                      country='US')
        self.register('Agilent', 'Agilent Technologies',
                      url='https://www.agilent.com',
                      country='US')
        self.register("D2DCRC", "Data to Decisions CRC",
                      url='https://www.d2dcrc.com.au', enabled=False)
        self.register("ClimateExtremes",
                      "ARC Centre of Excellence for Climate Extremes",
                      url='https://climateextremes.org.au')
        self.register('AAPP', "The Australian Antarctic Program Partnership",
                      url='https://aappartnership.org.au')
        self.register('agp', "Antarctic Gateway Partnership",
                      url='https://www.imas.utas.edu.au/'
                      'antarctic-gateway-partnership',
                      enabled=False)
        self.register('CHOMNZ',
                      "Centre for Health Outcome Measures New Zealand",
                      url='https://www.chomnz.org.nz',
                      country='NZ')
        self.register('CoEDL',
                      "ARC Centre of Excellence for the Dynamics of Language",
                      url='https://www.dynamicsoflanguage.edu.au')
        self.register('AgriFutures', "AgriFutures Australia",
                      url='https://www.agrifutures.com.au')
        self.register('inovaschar', 'Inova Schar Cancer Institute (USA)',
                      url='https://www.inova.org/our-services/'
                      'inova-schar-cancer-institute')
        self.register('njernda', "Njernda Aboriginal Corporation",
                      url='https://www.njernda.com.au')
        self.register('AIC', "Australia–Indonesia Centre",
                      url='https://australiaindonesiacentre.org')
        self.register('ACT', "Australian Capital Territory Government")
        self.register('TAS', "State Government of Tasmania")
        self.register('NRE',
                      'Department of Natural Resources and '
                      'Environment Tasmania',
                      url="https://nre.tas.gov.au",
                      parent=self.reg_map['tas'])
        self.register('DPIPWE',
                      'Department Primary Industries, Parks, Water '
                      'and Environment',
                      url='https://dpipwe.tas.gov.au',
                      parent=self.reg_map['tas'],
                      successor=self.reg_map['nre'])
        self.register('Rumbalara', "Rumbalara Aboriginal Cooperative",
                      url='https://rumbalara.org.au')
        self.register('ERH', "Echuca Regional Health",
                      url='https://erh.org.au')
        self.register('campaspe', "Campaspe Shire Council",
                      url='https://www.campaspe.vic.gov.au')
        self.register('ANZCVS', "Australian and New Zealand College of "
                      "Veterinary Scientists",
                      url='https://www.anzcvs.org.au')
        self.register('RBG', "Royal Botanic Gardens Victoria",
                      url='https://www.rbg.vic.gov.au',
                      parent=self.name_map['Government of Victoria'])
        self.register('Netcare', "NetCare Group Ltd", country='ZA',
                      url='https://www.netcare.co.za')
        self.register('FirstLanguages', "First Languages Australia",
                      url='https://www.firstlanguages.org.au')
        self.register('ARCS', "Australian Rainforest Conservation Society",
                      url='https://rainforest.org.au')
        self.register('ForestsAlive', "Forests Alive Pty Ltd")  # No url found
        self.register('APCRC-Q', "Australian Prostate Cancer Research Centre",
                      url='http://www.australianprostatecentre.org')
        self.register('InvertebratesAU', "Invertebrates Australia Ltd",
                      url='https://invertebratesaustralia.org')
        self.register('LandSolution', "Land Solution Australia",
                      url='https://www.landsolution.com.au')
        self.register('CTx',
                      "Cooperative Research Centre for Cancer Therapeutics",
                      enabled=False)
        self.register('FPA', "Forest Practices Authority Tasmania",
                      url='https://www.fpa.tas.gov.au',
                      parent=self.reg_map['tas'])
        self.register('QVMAG', "Queen Victoria Museum and Art Gallery",
                      url='https://www.qvmag.tas.gov.au',
                      parent=self.reg_map['tas'])
        self.register('RCH', "Royal Children's Hospital, Melbourne",
                      url='https://www.rch.org.au')
        self.register('stt', "Sustainable Timber Tasmania",
                      url='https://sttas.com.au',
                      parent=self.reg_map['tas'])
        self.register('NADC', "National Association of Diabetes Centres",
                      url='https://nadc.net.au')
        self.register('DTA', 'Digital Transformation Agency',
                      parent=self.name_map["Australian Government"])
        self.register('MA', "Metabalomics Australia",
                      url='https://www.metabolomics.net.au')
        self.register('Phoenix', "Phoenix Australia",
                      url='https://www.phoenixaustralia.org')
        self.register('Shepparton', "Greater Shepparton City Council",
                      url='https://greatershepparton.com.au')
        self.register('RACE', "RACE for 2030 CRC",
                      url='https://www.racefor2030.com.au')
        self.register('NaturalHazards', "Natural Hazards Research Australia",
                      url='https://www.naturalhazards.com.au')
        self.register('NGHV', "National Geriatric Hospital of Vietnam",
                      country='VN')
        self.register('SOOS', "Southern Ocean Observing System",
                      country='AQ', url='https://www.soos.aq')
        self.register('Burnett', "South Burnett Regional Council",
                      url='https://www.southburnett.qld.gov.au')
        self.register('NRMSouth', 'NRM South', url='https://nrmsouth.org.au')
        self.register('TMAG', 'Tasmania Museum and Art Gallery',
                      url='https://www.tmag.tas.gov.au',
                      parent=self.reg_map['tas'])
        self.register('VicForests', "VicForests",
                      url='https://www.vicforests.com.au',
                      parent=self.name_map['Government of Victoria'])
        self.register('VicNode', "VicNode", enabled=False)
        self.register('AFAC',
                      "National Council for Fire and Emergency Services",
                      url='https://www.afac.com.au')
        self.register('TPAC', "Tasmanian Partnership for Advanced Computing",
                      url='https://www.tpac.org.au')
        self.register("ACS", "Australian Computer Society",
                      url='https://info.acs.org.au')
        self.register("QMN", "Queensland Museum Network",
                      url='https://www.museum.qld.gov.au/')
        self.register("NHFIC", "National Housing Finance and "
                      "Investment Corporation",
                      parent=self.name_map["Australian Government"],
                      url="https://www.nhfic.gov.au/")
        self.register("FrontierSI", "Frontier SI",
                      url="https://frontiersi.com.au/")


class BaseOrgMatcher(LocalOrganisationMappings):

    name_map = {}
    alias_map = {}
    acronym_map = {}
    lc_name_map = {}
    lc_alias_map = {}
    lc_acronym_map = {}
    n_name_map = {}
    n_alias_map = {}
    n_acronym_map = {}
    ambiguous_acronyms = []
    ambiguous_aliases = []
    reverse_map = {}
    reg_map = {}
    lc_reg_map = {}

    def __init__(self, catalog):
        super().__init__(catalog)

    def load_maps(self, dump_url):
        matches = 0
        with utils.open_config_file(dump_url) as fp:
            ror_data = json.load(fp)
            for ror in ror_data:
                if ror['country']['country_code'] in {'AU', 'NZ'}:
                    # Only use aliases and acronyms for "local" orgs.
                    # If we consider ambiguities with overseas orgs we
                    # lose a lot of hits ...
                    for alias in ror['aliases']:
                        # Cruft filter ...
                        if not re.match(r'^[\w\s]{2,}$', alias):
                            continue
                        if alias in self.alias_map:
                            self.ambiguous_aliases.append(alias)
                        else:
                            self.alias_map[alias] = ror['id']
                    for acronym in ror['acronyms']:
                        # Cruft filter ...
                        if not re.match(r'^[\w\s]{2,}$', acronym):
                            continue
                        if acronym in self.acronym_map:
                            self.ambiguous_acronyms.append(acronym)
                        else:
                            self.acronym_map[acronym] = ror['id']
                else:
                    # If this is non-local and there is full-name ambiguity,
                    # don't use it.  (Example: "Victoria University")
                    if ror['name'] in self.name_map:
                        continue

                self.name_map[ror['name']] = ror['id']
                self.reverse_map[ror['id']] = ror['name']

        for a in self.ambiguous_acronyms:
            if a in self.acronym_map:
                del self.acronym_map[a]
        for a in self.ambiguous_aliases:
            if a in self.alias_map:
                del self.alias_map[a]

        LOG.info(f"{matches} matches, {len(self.name_map)} organisation names")
        LOG.info(f"{len(self.alias_map)} aliases")
        LOG.info(f"{len(self.acronym_map)} acronyms")

    def secondary_maps(self):
        self.lc_name_map = {
            k.lower(): v for (k, v) in self.name_map.items()}
        self.lc_alias_map = {
            k.lower(): v for (k, v) in self.alias_map.items()}
        self.lc_acronym_map = {
            k.lower(): v for (k, v) in self.acronym_map.items()}
        self.lc_reg_map = {
            k.lower(): v for (k, v) in self.reg_map.items()}

        self.n_name_map = {
            tuple(self.normalize(k)): v for (k, v) in self.name_map.items()}
        self.n_name_map.update({
            tuple(self.normalize(k, sort=False)): v
            for (k, v) in self.name_map.items()})

        self.n_alias_map = {
            tuple(self.normalize(k)): v for (k, v) in self.alias_map.items()}
        self.n_alias_map.update({
            tuple(self.normalize(k, sort=False)): v
            for (k, v) in self.alias_map.items()})

        self.n_acronym_map = {
            tuple(self.normalize(k)): v
            for (k, v) in self.acronym_map.items()}
        self.n_acronym_map.update({
            tuple(self.normalize(k, sort=False)): v
            for (k, v) in self.acronym_map.items()})

    def plain_match(self, text):
        if text in self.name_map:
            return self.name_map[text]
        elif text in self.alias_map:
            return self.alias_map[text]
        elif text in self.acronym_map:
            return self.acronym_map[text]
        elif text in self.reg_map:
            return self.reg_map[text]
        else:
            return None

    def lc_match(self, text):
        text = text.lower()
        if text in self.lc_name_map:
            return self.lc_name_map[text]
        elif text in self.lc_alias_map:
            return self.lc_alias_map[text]
        elif text in self.lc_acronym_map:
            return self.lc_acronym_map[text]
        elif text in self.lc_reg_map:
            return self.lc_reg_map[text]
        else:
            return None

    def full_match(self, text):
        return self.plain_match(text) or self.lc_match(text)

    def normalize(self, text, sort=True):
        split = re.split(r'\W+', text)
        words = [s.lower() for s in split if s.lower() not in self.noise]
        if sort:
            words = sorted(words)
        return words

    def heuristic_match(self, text):
        """Applies spelling corrections, removes noise words,
        removes stuff in parentheses, discards punctuation
        and ignores case.
        """

        text = re.sub(r'\s*\(.*\)\s*', '', text)
        text = self.normalize(text)
        for i in range(0, len(text)):
            if text[i] in self.s_map:
                text[i] = self.s_map[text[i]]
        text = tuple(text)

        if text in self.n_name_map:
            return self.n_name_map[text]
        elif text in self.n_alias_map:
            return self.n_alias_map[text]
        elif text in self.n_acronym_map:
            return self.n_acronym_map[text]
        else:
            return None

    def record_match(self, *args, **kwargs):
        pass

    def register(self, *args, **kwargs):
        pass

    def do_matching(self, institution, **kwargs):
        institution = institution.strip()
        if match := self.full_match(institution):
            self.record_match(institution, match, **kwargs)
            return True
        if match := self.heuristic_match(institution):
            self.record_match(institution, match, type="heuristic", **kwargs)
            return True
        if '@' not in institution:  # ... not in email addresses
            split = re.split('[,;/.|&-]', institution)
            if len(split) > 1:
                partial_match = False
                for s in split:
                    s = s.strip()
                    if match := self.full_match(s):
                        self.record_match(institution, match,
                                          partial=s, **kwargs)
                        partial_match = True
                    elif match := self.heuristic_match(s):
                        self.record_match(institution, match, partial=s,
                                          type="heuristic", **kwargs)
                        partial_match = True
                if partial_match:
                    return True
        m = re.search(r'\((.*)\)', institution)
        if m:
            if match := self.full_match(m.group(1)):
                self.record_match(institution, match,
                                  partial=m.group(1), **kwargs)
                return True
            elif match := self.heuristic_match(m.group(1)):
                self.record_match(institution, match,
                                  partial=m.group(1),
                                  type="heuristic", **kwargs)
                return True

        if match := self.fixup(institution):
            self.record_match(institution, match, type="fixup", **kwargs)
            return True
        return False


class TrialMatcher(BaseOrgMatcher):

    res = {}

    def __init__(self, catalog):
        super().__init__(catalog)

    def record_match(self, text, match, type=None, partial=None):
        if type:
            type = f"Partial {type}" if partial else f"Full {type}"
        else:
            type = "Partial" if partial else "Full"
        if partial:
            print(f"{type} match for {text} (({partial})) -> {match}")
        else:
            print(f"{type} match for {text} -> {match}")
        if match in [
                'none',
                self.name_map['Australian Research Council'],
                self.name_map['National Health and Medical Research Council']]:
            self.res[text] = None
        elif partial:
            v = self.res.get(text, [])
            for m in match if isinstance(match, list) else [match]:
                if m not in v:
                    v.append(m)
            self.res[text] = v
        else:
            if text in self.res:
                raise Exception(f"duplicate for {text}")
            self.res[text] = match

    def register(self, short, full, url=None, successor=None, parent=None,
                 country='AU', enabled=True, ror=None):
        key = short.lower()
        if key in self.reg_map:
            raise Exception('duplicate registration')
        enabled = enabled and successor is not None
        record = {'short': short, 'full': full, 'url': url,
                  'successor': successor, 'parent': parent,
                  'enabled': enabled, 'country': country,
                  'ror': ror}
        self.name_map[full] = record
        self.reg_map[key] = record
        self.acronym_map[short] = record

    def _show(self, v):
        if isinstance(v, str):
            if v.startswith("http"):
                if v in self.reverse_map:
                    return f"{v} ({self.reverse_map[v]})"
                else:
                    return v
            else:
                return f"{v} ({self.reg_map[v]['full']})"
        elif isinstance(v, list):
            return f"[{', '.join([self._show(vv) for vv in v])}]"
        else:
            return str(v)

    def run(self, dump_url, institutions):
        self.load_maps(dump_url)
        self.registrations()
        self.secondary_maps()
        for institution in institutions:
            institution = institution.strip()
            if institution in self.res:
                continue
            if not self.do_matching(institution):
                print(f"No matches for {institution}")

        print("=======================================================")
        for (k, v) in self.res.items():
            print(f"'{k}' -> {self._show(v)}")


class Migrater(BaseOrgMatcher):

    def __init__(self, catalog):
        super().__init__(catalog)

    def get_mapped_org(self, key):
        if isinstance(key, self.catalog.Organisation):
            return key
        elif key.lower() in self.reg_map:
            return self.reg_map[key.lower()]
        else:
            try:
                return self.catalog.Organisation.objects.get(ror_id=key)
            except exceptions.ObjectDoesNotExist:
                LOG.error(f"No Organisation with ROR id {key}")
            except exceptions.MultipleObjectsReturned:
                LOG.error(f"Multiple Organisations with ROR id {key}")

    def register(self, short, full, url="", successor=None, parent=None,
                 country='AU', enabled=True, ror=""):
        (system, created) = self.catalog.Approver.objects.get_or_create(
            username="system", defaults={'display_name': 'System Approver'})
        (org, created) = self.catalog.Organisation.objects.update_or_create(
            short_name=short, full_name=full,
            url=url, enabled=enabled, country=country, vetted_by=system)
        self.reg_map[short.lower()] = org
        self.reg_map[full] = org
        if parent:
            org.parent = self.get_mapped_org(parent)
        if not created:
            org.supercedes.clear()
        if successor:
            org.supercedes.add(self.get_mapped_org(successor))
        if parent or successor or not created:
            org.save()

    def _get_parent_id(self, allocation):
        if allocation:
            if allocation.parent_request:
                return allocation.parent_request.id
            else:
                return allocation.id
        else:
            return None

    def record_match(self, text, match, ci=None, allocation=None, **kwargs):
        if isinstance(match, list):
            deduped_matches = []
            for m in match:
                if m not in deduped_matches:
                    deduped_matches.append(m)
            # Recurse ...
            for m in deduped_matches:
                self.record_match(text, m, ci=ci, allocation=allocation,
                                  **kwargs)
            return

        if isinstance(match, str):
            if match.startswith("https://ror.org"):
                org = self.catalog.Organisation.objects.get(ror_id=match)
            elif match == "nothing":
                org = None
            else:
                org = self.reg_map[match]
        elif isinstance(match, dict):
            # Deal with the case where the same text maps to
            # different organisations in different contexts.
            if allocation:
                parent_id = self._get_parent_id(allocation)
            elif ci:
                parent_id = self._get_parent_id(ci.allocation)
            if match['parent_id'] == parent_id:
                org = self.catalog.Organisation.objects.get(
                    ror_id=match['ror'])
            else:
                # Not a match in this context ...
                org = None
        else:
            org = match
        if org:
            if org.short_name == self.catalog.ORG_UNKNOWN_SHORT_NAME:
                if allocation:
                    print(f"Using org {self.catalog.ORG_UNKNOWN_SHORT_NAME} "
                          f"for allocation {allocation.id} "
                          f"(parent {allocation.parent_request})")
                if ci:
                    print(f"Using org {self.catalog.ORG_UNKNOWN_SHORT_NAME} "
                          f"for CI {ci.id} for allocation {ci.allocation.id} "
                          f"(parent {ci.allocation.parent_request})")
            if allocation:
                allocation.supported_organisations.add(org)
                utils.save_allocation_without_updating_timestamps(allocation)
            if ci:
                ci.primary_organisation = org
                ci.save()

    def run(self, dump_url):
        self.load_maps(dump_url)
        LOG.info("Registering additional organisations")
        self.registrations()
        self.secondary_maps()
        LOG.info("Migrating allocation institutions")
        count = 0
        for i in self.catalog.Institution.objects.all() \
                            .prefetch_related('allocation'):
            self.do_matching(i.name, allocation=i.allocation)
            count += 1
            if (count % 10000) == 0:
                LOG.info(f"Processed {count} allocation records")
        LOG.info(f"Completed processing {count} allocation records")
        LOG.info("Migrating CI institutions")
        count = 0
        for ci in self.catalog.ChiefInvestigator.objects.all():
            self.do_matching(ci.institution, ci=ci)
            count += 1
            if (count % 10000) == 0:
                LOG.info(f"Processed {count} CI records")
        LOG.info(f"Completed processing {count} CI records")
