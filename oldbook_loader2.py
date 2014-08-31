#!/usr/bin/env python
# vi:fileencoding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from django.db.models import get_model
from decimal import Decimal as D

Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
ProductCategory = get_model('catalogue', 'ProductCategory')
StockRecord = get_model('partner', 'StockRecord')
Partner = get_model('partner', 'Partner')
AttributeEntity = get_model('catalogue', 'AttributeEntity')
ProductAttribute = get_model('catalogue', 'ProductAttribute')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
ProductClass = get_model('catalogue', 'ProductClass')
ProductImage = get_model('catalogue', 'ProductImage')


get_upc = lambda cnt: "{0:06}".format(cnt)
practica = Partner.objects.get(pk=1)
paper_book = ProductClass.objects.get(pk=1)
series_cat = Category.objects.get(name="Серии")


attr_codes = ('additional', 'editors', 'year',
              'translation', 'subtitle', 'format')
attr_names = ("Дополнительно", "Редакторы", "Год", "Перевод", "Подзаголовок",
              "Формат")


def prep_attrs():
    for code, name in zip(attr_codes, attr_names):
        ProductAttribute.objects.get_or_create(name=name, code=code,
                                               product_class=paper_book)


def main(books):
    prep_attrs()
    book_count = 0
    for category in books:
        try:
            cat = Category.objects.get(name=category['title'])
        except Category.DoesNotExist:
            cat = series_cat.add_child(name=category['title'])
        for book in category['books']:
            if book['absent']:
                continue
            book_count += 1
            upc = get_upc(book_count)
            newbook, created = Product.objects.\
                get_or_create(upc=upc,
                              title=book['title'],
                              authors=book.get('authors', ''),
                              description=book.get('annotation', ''),
                              slug=book['slug'],
                              defaults=dict(
                                  contents=book.get('contents', ''),
                                  product_class=paper_book
                              ))
            if created:
                catrecord = ProductCategory(category=cat, product=newbook)
                catrecord.save()
                sr = StockRecord(
                    partner=practica,
                    price_excl_tax=D(book.get('price', 0)),
                    product=newbook,
                    num_in_stock = 1000,
                    partner_sku=upc
                )
                sr.save()
                for code in attr_codes:
                    if code in book and book[code]:
                        attribute = ProductAttribute.objects.get(code=code)
                        _type = attribute.type
                        value = book[code]
                        if _type == u'integer':
                            value = int(value)
                        attribrecord = ProductAttributeValue(
                            attribute = attribute,
                            product = newbook,
                            value = value)
                        attribrecord.save()
                _format = ""
                if 'page_count' in book and book['page_count']:
                    _format += "%s страниц. " % book['page_count']
                if 'cover' in book and book['cover']:
                    _format += "%s. " % book['cover']
                if _format:
                    attribute = ProductAttribute.objects.get(code='format')
                    attribrecord = ProductAttributeValue(
                        attribute=attribute,
                        product=newbook,
                        value=_format)
                    attribrecord.save()

if __name__ == '__main__':
    import sys
    bookpath = sys.argv[1]
    from os.path import exists
    if exists(bookpath):
        from json import load
        with open(bookpath, 'r') as f:
            main(load(f))
