# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'OrderAndItemCharges'
        db.delete_table(u'shipping_orderanditemcharges')

        # Removing M2M table for field countries on 'OrderAndItemCharges'
        db.delete_table(db.shorten_name(u'shipping_orderanditemcharges_countries'))

        # Deleting model 'WeightBand'
        db.delete_table(u'shipping_weightband')

        # Deleting model 'WeightBased'
        db.delete_table(u'shipping_weightbased')

        # Removing M2M table for field countries on 'WeightBased'
        db.delete_table(db.shorten_name(u'shipping_weightbased_countries'))

        # Adding model 'FixedPriceShipping'
        db.create_table(u'shipping_fixedpriceshipping', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('oscar.models.fields.autoslugfield.AutoSlugField')(allow_duplicates=False, max_length=128, separator=u'-', blank=True, unique=True, populate_from=u'name', overwrite=False)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('line1', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('line2', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('line3', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('line4', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('postcode', self.gf('oscar.models.fields.UppercaseCharField')(max_length=64, blank=True)),
            ('is_shortcut', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_sufficient', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('upper_weight_limit', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('free_shipping_threshold', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('price_per_order', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2)),
        ))
        db.send_create_signal(u'shipping', ['FixedPriceShipping'])

        # Adding M2M table for field countries on 'FixedPriceShipping'
        m2m_table_name = db.shorten_name(u'shipping_fixedpriceshipping_countries')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('fixedpriceshipping', models.ForeignKey(orm[u'shipping.fixedpriceshipping'], null=False)),
            ('country', models.ForeignKey(orm[u'address.country'], null=False))
        ))
        db.create_unique(m2m_table_name, ['fixedpriceshipping_id', 'country_id'])

        # Adding M2M table for field allows_payment_methods on 'FixedPriceShipping'
        m2m_table_name = db.shorten_name(u'shipping_fixedpriceshipping_allows_payment_methods')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('fixedpriceshipping', models.ForeignKey(orm[u'shipping.fixedpriceshipping'], null=False)),
            ('sourcetype', models.ForeignKey(orm[u'payment.sourcetype'], null=False))
        ))
        db.create_unique(m2m_table_name, ['fixedpriceshipping_id', 'sourcetype_id'])


    def backwards(self, orm):
        # Adding model 'OrderAndItemCharges'
        db.create_table(u'shipping_orderanditemcharges', (
            ('code', self.gf('oscar.models.fields.autoslugfield.AutoSlugField')(populate_from='name', allow_duplicates=False, max_length=128, separator=u'-', blank=True, unique=True, overwrite=False)),
            ('price_per_item', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('price_per_order', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2)),
            ('free_shipping_threshold', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True)),
        ))
        db.send_create_signal(u'shipping', ['OrderAndItemCharges'])

        # Adding M2M table for field countries on 'OrderAndItemCharges'
        m2m_table_name = db.shorten_name(u'shipping_orderanditemcharges_countries')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('orderanditemcharges', models.ForeignKey(orm[u'shipping.orderanditemcharges'], null=False)),
            ('country', models.ForeignKey(orm[u'address.country'], null=False))
        ))
        db.create_unique(m2m_table_name, ['orderanditemcharges_id', 'country_id'])

        # Adding model 'WeightBand'
        db.create_table(u'shipping_weightband', (
            ('charge', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=2)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('upper_limit', self.gf('django.db.models.fields.FloatField')()),
            ('method', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bands', to=orm['shipping.WeightBased'])),
        ))
        db.send_create_signal(u'shipping', ['WeightBand'])

        # Adding model 'WeightBased'
        db.create_table(u'shipping_weightbased', (
            ('code', self.gf('oscar.models.fields.autoslugfield.AutoSlugField')(populate_from='name', allow_duplicates=False, max_length=128, separator=u'-', blank=True, unique=True, overwrite=False)),
            ('default_weight', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('upper_charge', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True)),
        ))
        db.send_create_signal(u'shipping', ['WeightBased'])

        # Adding M2M table for field countries on 'WeightBased'
        m2m_table_name = db.shorten_name(u'shipping_weightbased_countries')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('weightbased', models.ForeignKey(orm[u'shipping.weightbased'], null=False)),
            ('country', models.ForeignKey(orm[u'address.country'], null=False))
        ))
        db.create_unique(m2m_table_name, ['weightbased_id', 'country_id'])

        # Deleting model 'FixedPriceShipping'
        db.delete_table(u'shipping_fixedpriceshipping')

        # Removing M2M table for field countries on 'FixedPriceShipping'
        db.delete_table(db.shorten_name(u'shipping_fixedpriceshipping_countries'))

        # Removing M2M table for field allows_payment_methods on 'FixedPriceShipping'
        db.delete_table(db.shorten_name(u'shipping_fixedpriceshipping_allows_payment_methods'))


    models = {
        u'address.country': {
            'Meta': {'ordering': "('-display_order', 'name')", 'object_name': 'Country'},
            'display_order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'is_shipping_country': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'iso_3166_1_a2': ('django.db.models.fields.CharField', [], {'max_length': '2', 'primary_key': 'True'}),
            'iso_3166_1_a3': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '3', 'blank': 'True'}),
            'iso_3166_1_numeric': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'printable_name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'payment.sourcetype': {
            'Meta': {'object_name': 'SourceType'},
            'code': ('oscar.models.fields.autoslugfield.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '128', 'separator': "u'-'", 'blank': 'True', 'unique': 'True', 'populate_from': "'name'", 'overwrite': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_defered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'shipping.fixedpriceshipping': {
            'Meta': {'ordering': "(u'pk',)", 'object_name': 'FixedPriceShipping'},
            'allows_payment_methods': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['payment.SourceType']", 'symmetrical': 'False', 'blank': 'True'}),
            'code': ('oscar.models.fields.autoslugfield.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '128', 'separator': "u'-'", 'blank': 'True', 'unique': 'True', 'populate_from': "u'name'", 'overwrite': 'False'}),
            'countries': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['address.Country']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'free_shipping_threshold': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_shortcut': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_sufficient': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'line1': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'line2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'line3': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'line4': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'postcode': ('oscar.models.fields.UppercaseCharField', [], {'max_length': '64', 'blank': 'True'}),
            'price_per_order': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'upper_weight_limit': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['shipping']