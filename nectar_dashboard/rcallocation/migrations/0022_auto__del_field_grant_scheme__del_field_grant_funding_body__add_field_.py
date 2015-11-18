# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Grant', fields ['allocation', 'grant_type', 'funding_body', 'scheme', 'grant_id', 'first_year_funded', 'total_funding']
        db.delete_unique(u'rcallocation_grant', ['allocation_id', 'grant_type', 'funding_body', 'scheme', 'grant_id', 'first_year_funded', 'total_funding'])

        # Deleting field 'Grant.scheme'
        db.delete_column(u'rcallocation_grant', 'scheme')

        # Deleting field 'Grant.funding_body'
        db.delete_column(u'rcallocation_grant', 'funding_body')

        # Adding field 'Grant.funding_body_scheme'
        db.add_column(u'rcallocation_grant', 'funding_body_scheme',
                      self.gf('django.db.models.fields.CharField')(default='arc', max_length=255),
                      keep_default=False)

        # Adding unique constraint on 'Grant', fields ['allocation', 'grant_type', 'funding_body_scheme', 'grant_id', 'first_year_funded', 'total_funding']
        db.create_unique(u'rcallocation_grant', ['allocation_id', 'grant_type', 'funding_body_scheme', 'grant_id', 'first_year_funded', 'total_funding'])


    def backwards(self, orm):
        # Removing unique constraint on 'Grant', fields ['allocation', 'grant_type', 'funding_body_scheme', 'grant_id', 'first_year_funded', 'total_funding']
        db.delete_unique(u'rcallocation_grant', ['allocation_id', 'grant_type', 'funding_body_scheme', 'grant_id', 'first_year_funded', 'total_funding'])

        # Adding field 'Grant.scheme'
        db.add_column(u'rcallocation_grant', 'scheme',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Grant.funding_body'
        db.add_column(u'rcallocation_grant', 'funding_body',
                      self.gf('django.db.models.fields.CharField')(default='arc', max_length=200),
                      keep_default=False)

        # Deleting field 'Grant.funding_body_scheme'
        db.delete_column(u'rcallocation_grant', 'funding_body_scheme')

        # Adding unique constraint on 'Grant', fields ['allocation', 'grant_type', 'funding_body', 'scheme', 'grant_id', 'first_year_funded', 'total_funding']
        db.create_unique(u'rcallocation_grant', ['allocation_id', 'grant_type', 'funding_body', 'scheme', 'grant_id', 'first_year_funded', 'total_funding'])


    models = {
        u'rcallocation.allocationrequest': {
            'Meta': {'object_name': 'AllocationRequest'},
            'allocation_home': ('django.db.models.fields.CharField', [], {'default': "'national'", 'max_length': '128'}),
            'approver_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'convert_trial_project': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'core_hours': ('django.db.models.fields.IntegerField', [], {'default': '744'}),
            'core_quota': ('django.db.models.fields.IntegerField', [], {'default': "'0'"}),
            'cores': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'end_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2016, 4, 30, 0, 0)'}),
            'estimated_number_users': ('django.db.models.fields.IntegerField', [], {'default': "'1'"}),
            'estimated_project_duration': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'field_of_research_1': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'field_of_research_2': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'field_of_research_3': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'for_percentage_1': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'for_percentage_2': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'for_percentage_3': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'funding_national_percent': ('django.db.models.fields.IntegerField', [], {'default': "'100'"}),
            'funding_node': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'geographic_requirements': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance_quota': ('django.db.models.fields.IntegerField', [], {'default': "'0'"}),
            'instances': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'modified_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'ncris_support': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'nectar_support': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'object_storage_zone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'parent_request': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rcallocation.AllocationRequest']", 'null': 'True', 'blank': 'True'}),
            'primary_instance_type': ('django.db.models.fields.CharField', [], {'default': "' '", 'max_length': '1', 'blank': 'True'}),
            'project_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ram_quota': ('django.db.models.fields.IntegerField', [], {'default': "'0'"}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'status_explanation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'submit_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'tenant_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'tenant_uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'usage_patterns': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'blank': 'True'}),
            'use_case': ('django.db.models.fields.TextField', [], {'max_length': '4096'}),
            'volume_zone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        u'rcallocation.chiefinvestigator': {
            'Meta': {'object_name': 'ChiefInvestigator'},
            'additional_researchers': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '1000', 'blank': 'True'}),
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'investigators'", 'to': u"orm['rcallocation.AllocationRequest']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'given_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        u'rcallocation.grant': {
            'Meta': {'unique_together': "(('allocation', 'grant_type', 'funding_body_scheme', 'grant_id', 'first_year_funded', 'total_funding'),)", 'object_name': 'Grant'},
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'grants'", 'to': u"orm['rcallocation.AllocationRequest']"}),
            'first_year_funded': ('django.db.models.fields.IntegerField', [], {'default': '2015'}),
            'funding_body_scheme': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'grant_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'grant_type': ('django.db.models.fields.CharField', [], {'default': "'arc'", 'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'total_funding': ('django.db.models.fields.FloatField', [], {})
        },
        u'rcallocation.institution': {
            'Meta': {'unique_together': "(('allocation', 'name'),)", 'object_name': 'Institution'},
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'institutions'", 'to': u"orm['rcallocation.AllocationRequest']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'rcallocation.publication': {
            'Meta': {'unique_together': "(('allocation', 'publication'),)", 'object_name': 'Publication'},
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'publications'", 'to': u"orm['rcallocation.AllocationRequest']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publication': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'rcallocation.quota': {
            'Meta': {'unique_together': "(('allocation', 'resource', 'zone'),)", 'object_name': 'Quota'},
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'quotas'", 'to': u"orm['rcallocation.AllocationRequest']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quota': ('django.db.models.fields.IntegerField', [], {'default': "'0'"}),
            'requested_quota': ('django.db.models.fields.IntegerField', [], {'default': "'0'"}),
            'resource': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'units': ('django.db.models.fields.CharField', [], {'default': "'GB'", 'max_length': '64'}),
            'zone': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['rcallocation']