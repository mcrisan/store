# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Product.price2'
        db.delete_column(u'webstore_product', 'price2')


    def backwards(self, orm):
        # Adding field 'Product.price2'
        db.add_column(u'webstore_product', 'price2',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)


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