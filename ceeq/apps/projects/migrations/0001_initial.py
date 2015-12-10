# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table(u'projects_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('jira_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('jira_version', self.gf('django.db.models.fields.CharField')(default='All Versions', max_length=200)),
            ('score', self.gf('django.db.models.fields.DecimalField')(default=109, max_digits=5, decimal_places=2)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('accuracy', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('suitability', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('interoperability', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('functional_security', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('usability', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('accessibility', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('technical_security', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('reliability', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('efficiency', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('maintainability', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('portability', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal(u'projects', ['Project'])

        # Adding model 'ProjectComponentsDefectsDensity'
        db.create_table(u'projects_projectcomponentsdefectsdensity', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('created', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('ceeq', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=5, decimal_places=3)),
            ('cxp', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=5, decimal_places=3)),
            ('platform', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=5, decimal_places=3)),
            ('reports', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=5, decimal_places=3)),
            ('application', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=5, decimal_places=3)),
            ('voiceSlots', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=5, decimal_places=3)),
        ))
        db.send_create_signal(u'projects', ['ProjectComponentsDefectsDensity'])

        # Adding model 'FrameworkParameter'
        db.create_table(u'projects_frameworkparameter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parameter', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('value', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=3, decimal_places=2)),
        ))
        db.send_create_signal(u'projects', ['FrameworkParameter'])


    def backwards(self, orm):
        # Deleting model 'Project'
        db.delete_table(u'projects_project')

        # Deleting model 'ProjectComponentsDefectsDensity'
        db.delete_table(u'projects_projectcomponentsdefectsdensity')

        # Deleting model 'FrameworkParameter'
        db.delete_table(u'projects_frameworkparameter')


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
            'created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'cxp': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'platform': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '3'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"}),
            'reports': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '3'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'voiceSlots': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '3'})
        }
    }

    complete_apps = ['projects']