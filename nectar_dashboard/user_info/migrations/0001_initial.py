# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2020-03-17 01:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import nectar_dashboard.user_info.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    # Special hack: if MANAGE_MODELS_FOR_TESTING is defined and True
    # in the Django settings, mark the 'User' model as managed so that
    # we can populate it in unit tests.  Otherwise, the model should
    # not be managed.  The real 'user' table is managed by RCShibboleth
    try:
        managed = settings.MANAGE_MODELS_FOR_TESTING
    except AttributeError:
        managed = False

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('persistent_id', models.CharField(blank=True, editable=False, help_text="The user's\n                                     eduPersonTargetedId", max_length=250, null=True, unique=True)),
                ('user_id', models.CharField(blank=True, help_text="The user's AAF user id\n                               supplied by their organization", max_length=64, null=True)),
                ('displayname', models.CharField(blank=True, help_text="The user's full name as\n                                   supplied by their organization", max_length=250, null=True)),
                ('email', models.CharField(blank=True, help_text="The user's authentic email\n                             address as supplied by their organization", max_length=250, null=True)),
                ('state', models.CharField(blank=True, choices=[('new', 'new'), ('registered', 'registered'), ('created', 'created')], default='new', editable=False, max_length=10, null=True)),
                ('terms_accepted_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('shibboleth_attributes', models.BinaryField(blank=True, null=True)),
                ('registered_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('terms_version', models.CharField(blank=True, editable=False, max_length=64, null=True)),
                ('ignore_username_not_email', models.IntegerField(blank=True, editable=False, null=True)),
                ('first_name', models.CharField(blank=True, help_text="The user's given name as\n                                  supplied by their organization", max_length=250, null=True)),
                ('surname', models.CharField(blank=True, help_text="The user's family name as\n                               supplied by their organization", max_length=250, null=True)),
                ('phone_number', nectar_dashboard.user_info.models.PhoneField(blank=True, help_text="The user's phone number", max_length=64, null=True)),
                ('mobile_number', nectar_dashboard.user_info.models.PhoneField(blank=True, help_text="The user's mobile number", max_length=64, null=True)),
                ('home_organization', models.CharField(blank=True, help_text="The user's primary\n                                         (home) organization", max_length=250, null=True)),
                ('orcid', models.CharField(blank=True, help_text="The user's orcid.", max_length=64, null=True)),
                ('affiliation', models.CharField(blank=True, choices=[('faculty', 'Faculty'), ('student', 'Student'), ('staff', 'Staff'), ('employee', 'Employee'), ('member', 'Member'), ('affiliate', 'Affiliate'), ('alum', 'Alumnus'), ('library-walk-in', 'Library walk-in')], default='member', help_text="The user's affiliation to\n                                   their home organization.  This needs\n                                   to be more specific than 'member'", max_length=64, null=True)),
            ],
            options={
                'db_table': 'user',
                'managed': managed,
            },
        ),
    ]
