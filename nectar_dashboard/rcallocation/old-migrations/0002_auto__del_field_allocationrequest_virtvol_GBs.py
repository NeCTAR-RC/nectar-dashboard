# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'AllocationRequest.virtvol_GBs'
        db.delete_column('rcallocation_allocationrequest', 'virtvol_GBs')


    def backwards(self, orm):
        
        # Adding field 'AllocationRequest.virtvol_GBs'
        db.add_column('rcallocation_allocationrequest', 'virtvol_GBs', self.gf('django.db.models.fields.IntegerField')(default='0'), keep_default=False)


    models = {
        'rcallocation.allocationrequest': {
            'Meta': {'object_name': 'AllocationRequest'},
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'core_hours': ('django.db.models.fields.IntegerField', [], {'default': "'100'"}),
            'cores': ('django.db.models.fields.IntegerField', [], {'default': "'1'"}),
            'created_by': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'end_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date(2012, 1, 16)'}),
            'geographic_requirements': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instances': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'object_storage_GBs': ('django.db.models.fields.IntegerField', [], {'default': "'0'"}),
            'primary_instance_type': ('django.db.models.fields.CharField', [], {'default': "'S'", 'max_length': '1'}),
            'project_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date(2012, 1, 16)'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'submit_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date(2012, 1, 16)'}),
            'usage_patterns': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'blank': 'True'}),
            'use_case': ('django.db.models.fields.TextField', [], {'max_length': '4096'})
        }
    }

    complete_apps = ['rcallocation']
