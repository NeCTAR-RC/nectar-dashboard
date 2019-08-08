# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-08-19 01:32
from __future__ import unicode_literals

from django.db import migrations

def populate(apps, schema_editor):
    Site = apps.get_model('rcallocation', 'Site')
    Approver = apps.get_model('rcallocation', 'Approver')
    sites = {}
    # The following is the list of known sites as at August 19th 2019.
    # Pawsey has 'gone', and there should be no Pawsey quotas remaining
    # in active allocations.  eRSA has been absorbed into TPAC, but there
    # still some remnant quotas
    for site in [('auckland', 'Auckland'),
                 ('ersa', 'eRSA'),
                 ('intersect', 'Intersect'),
                 ('monash', 'Monash'),
                 ('nci', 'NCI'),
                 ('pawsey', 'Pawsey'),
                 ('qcif', 'QCIF'),
                 ('swinburne', 'Swinburne'),
                 ('tpac', 'TPAC'),
                 ('uom', 'Melbourne')]:
        enabled = site[0] not in ['ersa', 'pawsey']
        sites[site[0]] = Site.objects.create(name=site[0],
                                             display_name=site[1],
                                             enabled=enabled)
    # The following is based on people with role 'AproveAdmin'
    # as at August 19th 2019.
    for approver in [('s.crawley@uq.edu.au',
                      'Stephen Crawley', 'qcif'),
                     ('r.burrowes@auckland.ac.nz',
                      'Robert Burrowes', 'auckland'),
                     ('justin.mammarella@unimelb.edu.au',
                      'Justin Mammarella', 'uom'),
                     ('jason.he@auckland.ac.nz',
                      'Jason He', 'auckland'),
                     ('lachlan.simpson@unimelb.edu.au',
                      'Lachlan Simpson', 'uom'),
                     ('stephen.welsh@monash.edu',
                      'Stephen Welsh', 'monash'),
                     ('Shahaan.Ayyub@monash.edu',
                      'Shahaan Ayyub', 'monash'),
                     ('bmeade@unimelb.edu.au',
                      'Bernard Meade', 'uom'),
                     ('n.ward4@uq.edu.au',
                      'Nigel Ward', 'qcif'),
                     ('dmilhuisen@swin.edu.au',
                      'Damien Milhuisen', 'swinburne'),
                     ('nhat.ngo1@unimelb.edu.au',
                      'Nhat Ngo', 'uom'),
                     ('gsauter@unimelb.edu.au',
                      'Greg Sauter', 'uom'),
                     ('sorrison@gmail.com',
                      'Sam Morrison', 'all'),
                     ('vul@unimelb.edu.au',
                      'Linh Vu', 'uom'),
                     ('nigel.williams@utas.edu.au',
                      'Nigel Williams', 'tpac'),
                     ('simon.fowler@anu.edu.au',
                      'Simon Fowler', 'nci'),
                     ('xiao.fu@utas.edu.au',
                      'Ming Fu', 'tpac'),
                     ('s.matheny@auckland.ac.nz',
                      'Sean Matheny', 'auckland'),
                     ('tsenga@unimelb.edu.au',
                      'Andy Tseng', 'uom'),
                     ('paul.coddington@unimelb.edu.au',
                      'Paul Coddington', 'all'),
                     ('shi.yan@unimelb.edu.au',
                      'Shi Yan', 'all'),
                     ('jake.yip@unimelb.edu.au',
                      'Jake Yip', 'all'),
                     ('andrew.botting@unimelb.edu.au',
                      'Andrew Botting', 'all'),
                     ('adrian.smith@unimelb.edu.au',
                      'Adrian Smith', 'all'),
                     ('elaine@intersect.org.au',
                      'Elaine Gully', 'intersect'),
                     ('swe.aung@monash.edu',
                      'Swe Aung', 'monash'),
                     ('sforsayeth@swin.edu.au',
                      'Simon Forsayeth', 'swinburne'),
                     ('rafael.lopez@monash.edu',
                      'Rafael Lopez', 'monash'),
                     ('Matthew.Armsby@utas.edu.au',
                      'Matt Armsby', 'tpac'),
                     ('Stephen.Dart@monash.edu',
                      'Stephen Dart', 'monash'),
                     ('r.todd@unimelb.edu.au',
                      'Richard Todd', 'uom'),
                     ('just.berkhout@utas.edu.au',
                      'Just Berkhout', 'tpac'),
                     ('gehendra@intersect.org.au',
                      'Gehendra Acharya', 'intersect'),
                     ('jerico.revote@monash.edu',
                      'Jericho Revote', 'monash'),
                     ('b.milford@uq.edu.au',
                      'Tim Rice', 'uom'),
                     ('alan.lo@unimelb.edu.au',
                      'Alan Lo', 'uom'),
                     ('m.feller@auckland.ac.nz',
                      'Martin Feller', 'auckland'),
                     ('j.morris@griffith.edu.au',
                      'Jo Morris', 'all'),
                     ('andrew.howard@anu.edu.au',
                      'Andrew Howard', 'nci'),
                     ('elyas.khan@unimelb.edu.au',
                      'Elyas Khan', 'uom'),
                     ('glenn@intersect.org.au',
                      'Glenn Satchell', 'intersect'),
                     ('dmc@unimelb.edu.au',
                      'Dylan Mcculloch', 'uom'),
                     ('israel@intersect.org.au',
                      'Israel Casas', 'intersect'),
                     ('mark.endrei@uq.edu.au',
                      'Mark Endrei', 'qcif'),
                     ('s.ansari@auckland.ac.nz',
                      'Sina Masoud-Ansari', 'auckland'),
                     ('wilfred.brimblecombe@unimelb.edu.au',
                      'Wilfred Brimblecombe', 'uom'),
                     ('s.bird@uq.edu.au',
                      'Stephen Bird', 'qcif'),
                     ('wei@intersect.org.au',
                      'Wei Fang', 'intersect')
                     ]:
        approver_object = Approver.objects.create(name=approver[0],
                                                  display_name=approver[1])
        if approver[2] == 'all':
            for site in sites.keys():
                approver_object.sites.add(sites[site])
        else:
            approver_object.sites.add(sites[approver[2]])


class Migration(migrations.Migration):

    dependencies = [
        ('rcallocation', '0036_sites_and_approvers'),
    ]

    operations = [
        migrations.RunPython(populate)
    ]
