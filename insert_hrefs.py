#!/usr/bin/env python
# vi:fileencoding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function


def insert_hrefs(books):
    from django.db.models import get_model, ObjectDoesNotExist
    Product = get_model('catalogue', 'Product')
    StockRecord = get_model('partner', 'StockRecord')
    Partner = get_model('partner', 'Partner')
    practica = Partner.objects.get(pk=1)
    ProductCategory = get_model('catalogue', 'ProductCategory')
    Category = get_model('catalogue', 'Category')
    main_list = Category.objects.get(name=u'На главной')

    i = 0
    for b in books:  # noqa
        if not 'href' in b: continue
        product = None
        found_by_name_collection = Product.objects.filter(title=b['title'])
        if len(found_by_name_collection) > 1:
            if 'subtitle' in b:
                found_by_subtitle = found_by_name_collection.filter(
                    attribute_values__value_text__exact=b['subtitle'])
                if found_by_subtitle.exists():
                    i += 1
                    product = found_by_subtitle.first()
        elif len(found_by_name_collection) == 1:
            i += 1
            product = found_by_name_collection[0]
        if product is not None:
            print(i, product)
            product.attr.redirect_href = b['href']
            product.attr.save()

if __name__ == '__main__':
    import sys, os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "practica.settings.dev")
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        import json
        with open(fname, 'r') as f:
            old_books = json.load(f)
        books = []
        for series in old_books:
            books += series['books']
        insert_hrefs(books)
