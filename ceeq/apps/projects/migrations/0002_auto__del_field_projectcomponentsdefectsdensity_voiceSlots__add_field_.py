# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Renaming field 'ProjectComponentsDefectsDensity.voiceSlots' to 'ProjectComponentsDefectsDensity.voice_slots'
        db.rename_column(u'projects_projectcomponentsdefectsdensity', 'voiceSlots', 'voice_slots')

        # Adding field 'ProjectComponentsDefectsDensity.ceeq_closed'
        db.add_column(u'projects_projectcomponentsdefectsdensity', 'ceeq_closed',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=5, decimal_places=3),
                      keep_default=False)

    def backwards(self, orm):
        # Renaming field 'ProjectComponentsDefectsDensity.voice_slots' to 'ProjectComponentsDefectsDensity.voiceSlots'
        db.add_column(u'projects_projectcomponentsdefectsdensity', 'voice_slots', 'voiceSlots')

        # Deleting field 'ProjectComponentsDefectsDensity.ceeq_closed'
        db.delete_column(u'projects_projectcomponentsdefectsdensity', 'ceeq_closed')

    models = {
        u'projects.frameworkparameter': {
            'Meta': {'object_name': 'FrameworkParameter'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameter': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'value': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '3', 'decimal_places': '2'})
        },
        u'projects.project': {
            'Meta': {'object_name': 'Project'},
            'accessibility': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'accuracy': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'efficiency': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'functional_security': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interoperability': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'jira_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'jira_version': ('django.db.models.fields.CharField', [], {'default': "'All Versions'", 'max_length': '200'}),
            'maintainability': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'portability': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'reliability': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'score': ('django.db.models.fields.DecimalField', [], {'default': '109', 'max_digits': '5', 'decimal_places': '2'}),
            'suitability': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'technical_security': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'usability': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'projects.projectcomponentsdefectsdensity': {
            'Meta': {'ordering': "['created', 'version']", 'object_name': 'ProjectComponentsDefectsDensity'},
            'application': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '3'}),
            'ceeq': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '3'}),
            'ceeq_closed': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '3'}),
            'created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'cxp': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'platform': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '3'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"}),
            'reports': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '3'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'voice_slots': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '3'})
        }
    }

    complete_apps = ['projects']