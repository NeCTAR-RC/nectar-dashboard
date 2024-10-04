# Generated by Django 1.11.29 on 2021-04-07 05:22

from django.db import migrations

INITIAL_FACILITIES = [
    # Exclude ARDC
    ("Astronomy Australia Ltd", "AAL"),
    ("Atlas of Living Australia", "ALA"),
    ("AuScope", "AuScope"),
    ("Australian Centre for Disease Preparedness", "ACDP"),
    ("Australian National Fabrication Facility", "ANFF"),
    ("Australian Plant Phenomics Facility", "APPF"),
    ("Australian Urban Research Infrastructure Network", "AURIN"),
    ("Bioplatforms Australia", "BPA"),
    ("Heavy Ion Accelerators", "HIA"),
    ("Integrated Marine Observing System", "IMOS"),
    ("Microscopy Australia", "MA"),
    ("National Computational Infrastructure", "NCI"),
    ("National Deuteration Facility", "NDF"),
    ("National Imaging Facility", "NIF"),
    ("Nuclear Science Facilities", "NSF"),
    ("Pawsey Supercomputing Centre", "Pawsey"),
    ("Phenomics Australia", "PA"),
    ("Population Health Research Network", "PHRN"),
    ("Terrestrial Ecosystem Research Network", "TERN"),
    ("Therapeutic Innovation Australia", "TIA"),
    ("NCRIS Pilot project", "Pilot"),
    ("Other NCRIS support", "Other"),
]


class Migration(migrations.Migration):
    def addNCRISFacilities(apps, schema_editor):
        NCRISFacility = apps.get_model('rcallocation', 'NCRISFacility')
        for f in INITIAL_FACILITIES:
            NCRISFacility.objects.create(name=f[0], short_name=f[1])

    def removeNCRISFacilities(apps, schema_editor):
        NCRISFacility = apps.get_model('rcallocation', 'NCRISFacility')
        NCRISFacility.objects.all().delete()

    dependencies = [
        ('rcallocation', '0057_add_ncris_facilities'),
    ]

    operations = [
        migrations.RunPython(addNCRISFacilities, removeNCRISFacilities)
    ]
