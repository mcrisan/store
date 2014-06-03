# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table('webstore_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('webstore', ['Category'])

        # Adding model 'Product'
        db.create_table('webstore_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')()),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='products', to=orm['webstore.Category'])),
            ('image_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('webstore', ['Product'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table('webstore_category')

        # Deleting model 'Product'
        db.delete_table('webstore_product')


    models = {
        'webstore.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'webstore.product': {
            'Meta': {'object_name': 'Product'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'to': "orm['webstore.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'quantity': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['webstore']