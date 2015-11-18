# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'AllocationRequest.tenant_name'
        db.add_column('rcallocation_allocationrequest', 'tenant_name',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'AllocationRequest.tenant_name'
        db.delete_column('rcallocation_allocationrequest', 'tenant_name')


    models = {
        'rcallocation.allocationrequest': {
            'Meta': {'object_name': 'AllocationRequest'},
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'core_hours': ('django.db.models.fields.IntegerField', [], {'default': "'100'"}),
            'core_quota': ('django.db.models.fields.IntegerField', [], {'default': "'2'"}),
            'cores': ('django.db.models.fields.IntegerField', [], {'default': "'1'"}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'end_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 3, 5, 0, 0)'}),
            'field_of_research_1': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'field_of_research_2': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'field_of_research_3': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'for_percentage_1': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'for_percentage_2': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'for_percentage_3': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'geographic_requirements': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance_quota': ('django.db.models.fields.IntegerField', [], {'default': "'2'"}),
            'instances': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'object_storage_GBs': ('django.db.models.fields.IntegerField', [], {'default': "'0'"}),
            'primary_instance_type': ('django.db.models.fields.CharField', [], {'default': "'S'", 'max_length': '1'}),
            'project_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ram_quota': ('django.db.models.fields.IntegerField', [], {'default': "'4'"}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 3, 5, 0, 0)'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'submit_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 3, 5, 0, 0)'}),
            'tenant_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tenant_uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'usage_patterns': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'blank': 'True'}),
            'use_case': ('django.db.models.fields.TextField', [], {'max_length': '4096'})
        }
    }

    complete_apps = ['rcallocation']