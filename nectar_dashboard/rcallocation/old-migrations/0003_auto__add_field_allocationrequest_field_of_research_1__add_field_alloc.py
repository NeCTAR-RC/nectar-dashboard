# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'AllocationRequest.field_of_research_1'
        db.add_column('rcallocation_allocationrequest', 'field_of_research_1',
                      self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True),
                      keep_default=False)

        # Adding field 'AllocationRequest.for_percentage_1'
        db.add_column('rcallocation_allocationrequest', 'for_percentage_1',
                      self.gf('django.db.models.fields.IntegerField')(default=100),
                      keep_default=False)

        # Adding field 'AllocationRequest.field_of_research_2'
        db.add_column('rcallocation_allocationrequest', 'field_of_research_2',
                      self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True),
                      keep_default=False)

        # Adding field 'AllocationRequest.for_percentage_2'
        db.add_column('rcallocation_allocationrequest', 'for_percentage_2',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'AllocationRequest.field_of_research_3'
        db.add_column('rcallocation_allocationrequest', 'field_of_research_3',
                      self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True),
                      keep_default=False)

        # Adding field 'AllocationRequest.for_percentage_3'
        db.add_column('rcallocation_allocationrequest', 'for_percentage_3',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'AllocationRequest.field_of_research_1'
        db.delete_column('rcallocation_allocationrequest', 'field_of_research_1')

        # Deleting field 'AllocationRequest.for_percentage_1'
        db.delete_column('rcallocation_allocationrequest', 'for_percentage_1')

        # Deleting field 'AllocationRequest.field_of_research_2'
        db.delete_column('rcallocation_allocationrequest', 'field_of_research_2')

        # Deleting field 'AllocationRequest.for_percentage_2'
        db.delete_column('rcallocation_allocationrequest', 'for_percentage_2')

        # Deleting field 'AllocationRequest.field_of_research_3'
        db.delete_column('rcallocation_allocationrequest', 'field_of_research_3')

        # Deleting field 'AllocationRequest.for_percentage_3'
        db.delete_column('rcallocation_allocationrequest', 'for_percentage_3')


    models = {
        'rcallocation.allocationrequest': {
            'Meta': {'object_name': 'AllocationRequest'},
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'core_hours': ('django.db.models.fields.IntegerField', [], {'default': "'100'"}),
            'cores': ('django.db.models.fields.IntegerField', [], {'default': "'1'"}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'end_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 10, 1, 0, 0)'}),
            'field_of_research_1': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'field_of_research_2': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'field_of_research_3': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'for_percentage_1': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'for_percentage_2': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'for_percentage_3': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'geographic_requirements': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instances': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'object_storage_GBs': ('django.db.models.fields.IntegerField', [], {'default': "'0'"}),
            'primary_instance_type': ('django.db.models.fields.CharField', [], {'default': "'S'", 'max_length': '1'}),
            'project_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 10, 1, 0, 0)'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'submit_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 10, 1, 0, 0)'}),
            'usage_patterns': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'blank': 'True'}),
            'use_case': ('django.db.models.fields.TextField', [], {'max_length': '4096'})
        }
    }

    complete_apps = ['rcallocation']