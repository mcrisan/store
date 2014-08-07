# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FirstOrderDiscount'
        db.create_table(u'webstore_firstorderdiscount', (
            (u'promotion_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['webstore.Promotion'], unique=True, primary_key=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 7, 23, 0, 0), null=True, blank=True)),
        ))
        db.send_create_signal(u'webstore', ['FirstOrderDiscount'])


    def backwards(self, orm):
        # Deleting model 'FirstOrderDiscount'
        db.delete_table(u'webstore_firstorderdiscount')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'webstore.cart': {
            'Meta': {'object_name': 'Cart'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['webstore.Product']", 'through': u"orm['webstore.Cart_Products']", 'symmetrical': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'webstore.cart_products': {
            'Meta': {'object_name': 'Cart_Products'},
            'cart': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['webstore.Cart']"}),
            'date_added': ('django.db.models.fields.DateField', [], {}),
            'discount': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['webstore.Promotion']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['webstore.Product']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {})
        },
        u'webstore.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'webstore.coupon': {
            'Meta': {'object_name': 'Coupon', '_ormbases': [u'webstore.Promotion']},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'promotion_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['webstore.Promotion']", 'unique': 'True', 'primary_key': 'True'}),
            'volume': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'webstore.deliverydetails': {
            'Meta': {'object_name': 'DeliveryDetails'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'cart': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['webstore.Cart']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phonenumber': ('phonenumber_field.modelfields.PhoneNumberField', [], {'max_length': '128'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'webstore.discount': {
            'Meta': {'object_name': 'Discount', '_ormbases': [u'webstore.Promotion']},
            'end_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 7, 23, 0, 0)', 'null': 'True', 'blank': 'True'}),
            u'promotion_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['webstore.Promotion']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'webstore.firstorderdiscount': {
            'Meta': {'object_name': 'FirstOrderDiscount', '_ormbases': [u'webstore.Promotion']},
            'end_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 7, 23, 0, 0)', 'null': 'True', 'blank': 'True'}),
            u'promotion_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['webstore.Promotion']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'webstore.product': {
            'Meta': {'object_name': 'Product'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'to': u"orm['webstore.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'quantity': ('django.db.models.fields.IntegerField', [], {})
        },
        u'webstore.promotion': {
            'Meta': {'object_name': 'Promotion'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'percent': ('django.db.models.fields.FloatField', [], {}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['webstore.Product']", 'symmetrical': 'False'}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 7, 23, 0, 0)'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '1'})
        },
        u'webstore.rating': {
            'Meta': {'object_name': 'Rating'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['webstore.Product']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        u'webstore.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'hometown': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locale': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'photo_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'webstore.wishlist': {
            'Meta': {'object_name': 'WishList'},
            'date_created': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 7, 23, 0, 0)'}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['webstore.Product']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['webstore']