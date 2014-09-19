#!/usr/bin/env python
# vi:fileencoding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

def insert_prices(books):
    from django.db.models import get_model, ObjectDoesNotExist
    Product = get_model('catalogue', 'Product')
    StockRecord= get_model('partner', 'StockRecord')
    Partner = get_model('partner', 'Partner')
    practica = Partner.objects.get(pk=1)
    ProductCategory= get_model('catalogue', 'ProductCategory')
    Category= get_model('catalogue', 'Category')
    main_list = Category.objects.get(name=u'На главной')


    i = 0
    for b in books:  # noqa
        if not 'price' in b: continue
        product = None
        found_by_name_collection = Product.objects.filter(title=b['title'])
        if len(found_by_name_collection) > 1:
            for found_by_name in found_by_name_collection:
                try:
                    subtitle = found_by_name.attr.get_value_by_attribute(found_by_name.attr.get_attribute_by_code('subtitle'))
                except ObjectDoesNotExist:
                    continue
                if 'subtitle' in b:
                    if b['subtitle'] == subtitle.value:
                        i += 1
                        product = found_by_name
                        print i, found_by_name
        elif len(found_by_name_collection) == 1:
            i += 1
            product = found_by_name_collection[0]
            print i, found_by_name_collection[0]
        if product is not None:
            if not len(product.stockrecords.all()):
                product.stockrecords.add(StockRecord(partner=practica, product=product, partner_sku=product.upc, price_excl_tax=b['price']))
            if not ProductCategory.objects.filter(product=product, category=main_list).exists():
                cat = ProductCategory(product=product, category=main_list)
                cat.save()
