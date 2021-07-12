# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-04-07 05:22
from __future__ import unicode_literals

from django.db import migrations


PROGRAMS = [
    # Platforms initiative
    ("ARDC Platforms", "ARDC Platforms program"),
    ("ARDC DR", "ARDC Data retention program"),
    # National Data Assets initiative
    ("ARDC CN-NDA", "ARDC Cross-NCRIS National Data Assets program"),
    ("ARDC ADP", "ARDC Australian Data Partnerships program"),
    ("ARDC PSB", "ARDC Public Sector Bridges program"),
    ("ARDC EC", "ARDC Emerging Collections program"),
    ("ARDC IU", "ARDC Institutional Underpinnings program"),
    ("ARDC HSANDA", "Health Studies Australian National Data Assets program"),
    # Translational Research Data Challenges initiative
    ("ARDC BDC", "Bushfire Data Challenges program"),
]

ARDC = [
    # Current but unclassified
    ("ARDC Internal", "ARDC Internal projects"),
    ("ARDC Nectar Ops", "ARDC Nectar cloud ops"),
    ("Nectar Node Ops", "Nectar Node cloud ops"),
]

LEGACY = [
    # Old programs
    ("Nectar VLs", "Nectar Virtual Laboratory (VL) program"),
    ("Nectar DeVLs", "Nectar Data enhanced Virtual Laboratory (DeVL) program"),
    ("Nectar Other", "Other Nectar supported projects"),
    ("ANDS", "ANDS supported projects"),
    ("RDS / RDSI", "RDS / RDSI supported projects"),
]

PLATFORM_PROJECTS = [
    ("Air-Health SWS",
     "Scientific workflow system for environmental health impact assessments",
     "PL059"),
    ("TLCMap 2.0",
     "Time-Layered Cultural Map of Australia 2.0",
     "PL069"),
    ("E2AMLBD",
     "Environments to Accelerate Machine Learning Based Discovery",
     "PL107"),
    ("AIS",
     "An Australian Imaging Service: Melding the Clinical and Academic "
     "using a Distributed Federation of Enhanced XNATS",
     "PL102"),
    ("GMRT—AusSeabed",
     "Global Multi-Resolution Topography for Australian coastal and "
     "ocean models",
     "PL019"),
    ("FishID", "Transforming Australian aquatic ecosystem monitoring "
     "using AI",
     "PL071"),
    ("Open EcoAcoustics",
     "Open EcoAcoustics: A Platform to Manage, Share and Analyse "
     "Ecoacoustic Data",
     "PL050"),
    ("VARDC",
     "Veterinary and Animal Research Data Commons",
     "PL073"),
    ("EcoCommons", "EcoCommons Australia", "PL108"),
    ("AgReFed",
     "AgReFed: A platform for the transformation of agricultural research",
     "PL005"),
    ("AHDAP", "The Australian Housing Data Analytics Platform", "PL065"),
    ("Australian Cancer Data Network",
     "Australian Cancer Data Network: distributed learning from "
     "clinical data",
     "PL014"),
    ("AEDAPT",
     "Australian Electrophysiology Data Analytics PlaTform",
     "PL017"),
    ("Human Genomes Platform",
     "Global technologies and standards for sharing human genomics "
     "research data",
     "PL032"),
    ("G-ADOPT", "Geodynamic ADjoint Optimization PlaTform", "PL031"),
    ("Biosecurity Commons",
     "Biosecurity Commons - Intelligently Managing our Pests and Diseases",
     "PL021"),
    ("Secure eResearch Platform",
     "Scalable Governance, Control & Management of FAIR Sensitive "
     "Research Data",
     "PL058"),
    ("ATAP", "Australian Text Analytics Platform", "PL074"),
    ("Australian Digital Observatory",
     "Australian Digital Observatory: Infrastructure for Dynamic Digital Data",
     "PL015"),
    ("ACCS", "The Australian Characterisation Commons at Scale", "PL101"),
    ("ASDC", "Establishing Australia's Scalable Done Cloud (ASDC)", "PL103"),
    ("ERICA",
     "E-Research Institutional Cloud Architecture (ERICA): "
     "Secure cloud computing for sensitive microdata",
     "PL109"),
    ("FAIMS 3.0",
     "FAIMS 3.0 Electronic Field Notebooks: A Platform for field research "
     "supporting digital capture and management in diverse situations",
     "PL110"),
    ("BioCommons BYOD",
     "The BioCommons BYOD Expansion Project "
     "(Integrating instruments, analysis tools and compute platforms for "
     "leadership bioinformatics",
     "PL105"),
    ("ATRC", "The Australian Transport Research Cloud (ATRC)", "PL104"),
    ("CADRE",
     "Coordinated Access for Data, Researchers and Environments (CADRE) "
     "- A Five Safes Implementation Framework for Sensitive Data in HASS",
     "PL106")
    ]

NDA_PROJECTS = [
    ("XN001", "OzBarley: from genome to phenome and back again"),
    ("XN002",
     "Building a National High-Resolution Geophysics Reference Collection "
     "for 2030 Computation"),
    ("XN003",
     "Integrating clinical and experimental genotype-phenotype data for "
     "biomedical discovery and disease management"),
    ("XN004",
     "Data nexus: coupling genomic and oceanographic data to enhance "
     "integration"),
    ("XN005",
     "Ecosystem data integration to support national environmental reporting"),
    ("XN006",
     "A National Scale Data Asset to Integrate Molecular Imaging "
     "with Bio-analytic"),
    ("XN007", "Australian Urban Health Indicators"),
    ("DP793", "The LINked Data Asset for Australian Health Research"),
    ("DP718",
     "Australian and New Zealand Leaders, Elections and Democracy Data Asset"),
    ("DP727", "Australian Invasive Species and Pest Genome Partnership"),
    ("DP713", "Advancing the Australian Companion Animal Registry of Cancers"),
    ("DP768", "Language Data Commons of Australia"),
    ("DP720",
     "AusTraits: a national database on the traits of Australia’s "
     "complete flora"),
    ("DP723", "Australasian Computational and Simulation Commons"),
    ("DP708", "A national transfusion data asset for Australia"),
    ("DP761",
     "Harnessing fish and shark image data for powerful biodiversity "
     "reporting"),
    ("DP735",
     "Boosting public health research with a national poisoning dataset"),
    ("DP728", "Australian National Child Health and Development Atlas"),
    ("DP748",
     "Development of a National Infrastructure for in-situ wave observations"),
    ("DP702",
     "A comprehensive national scale human mobility data asset for Australia"),
    ("PS022", "Integrated national air pollution and health data"),
    ("PS027",
     "Sensitive Species Data Pathways from Decision Making to Research"),
    ("PS031",
     "Leveraging data to support young people’s education and wellbeing"),
    ("PS014", "Hospital EMR data as a National Data Asset for Research"),
    ("PS010",
     "National Free Access Coronial Findings, Recommendations & Responses"),
]

VL_PROJECTS = [
    # Virtual Laboratory projects
    ("Alveo", "A Virtual Lab for Human Communication Science"),
    ("ASVO", "All-Sky Virtual Observatory"),
    ("BCCVL", "Biodiversity and Climate Change Virtual Laboratory"),
    ("CVL", "Characterization Virtual Laboratory"),
    ("CWSLab", "Climate and Weather Science Lab"),
    ("FAIMS", "Field Acquired Information Management Systems"),
    ("GVL", "Genomics Virtual Laboratory"),
    ("HuNI", "Humanities Networked Infrastructure"),
    ("IEL", "Industrial Ecology Lab"),
]


# Default ranking for the main menu
PLATFORM_MENU_GROUP = 10
NDA_MENU_GROUP = 20
VL_MENU_GROUP = 30
PROGRAM_MENU_GROUP = 40
ARDC_MENU_GROUP = 50
LEGACY_MENU_GROUP = 60
FINAL_MENU_GROUP = 70



class Migration(migrations.Migration):

    def addARDCSupport(apps, schema_editor):
        ARDCSupport = apps.get_model('rcallocation', 'ARDCSupport')
        for p in PROGRAMS:
            ARDCSupport.objects.create(
                name=p[1], short_name=p[0],
                project=False, explain=True, rank=PROGRAM_MENU_GROUP)
        for p in PLATFORM_PROJECTS:
            ARDCSupport.objects.create(
                name=p[1], short_name=p[0],
                project_id=p[2], rank=PLATFORM_MENU_GROUP)
        # The NDA projects don't have designated short names, but we
        # use the short_name option values.  So we use the project ids
        # as the short names.
        for p in NDA_PROJECTS:
            ARDCSupport.objects.create(
                name=p[1], short_name=p[0],
                project_id=p[0], rank=NDA_MENU_GROUP)
        for p in VL_PROJECTS:
            ARDCSupport.objects.create(
                name=p[1], short_name=p[0], rank=VL_MENU_GROUP)
        for p in ARDC:
            ARDCSupport.objects.create(
                name=p[1], short_name=p[0],
                project=False, explain=True, 
                rank=ARDC_MENU_GROUP)
        for p in LEGACY:
            ARDCSupport.objects.create(
                name=p[1], short_name=p[0],
                project=False, explain=True, 
                rank=LEGACY_MENU_GROUP)
        # The "Other" catch-all
        ARDCSupport.objects.create(
                name="Other projects not covered above",
                short_name='Other',
                project=False, explain=True, 
                rank=FINAL_MENU_GROUP)

    def removeARDCSupport(apps, schema_editor):
        ARDCSupport = apps.get_model('rcallocation', 'ARDCSupport')
        ARDCSupport.objects.all().delete()

    dependencies = [
        ('rcallocation', '0059_add_ardc_support'),
    ]

    operations = [
        migrations.RunPython(addARDCSupport, removeARDCSupport)
    ]
