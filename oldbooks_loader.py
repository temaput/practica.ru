#set encoding=utf-8
from django.db.models import get_model
from decimal import Decimal as D
from django.core.files import File
from os.path import join

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
old_site_path = "/home/tema/html/practica.ru/docs/Books"
get_cover_file = lambda path: join(old_site_path, path)
get_category_path = lambda cnt: "{0:08}".format(cnt + 10000)
practica = Partner.objects.get(pk=1)
paper_book = ProductClass.objects.get(pk=1)
series_cat = Category.objects.get(pk=1)

soft_cover = AttributeEntity.objects.get(slug='soft_cover')
hard_cover = AttributeEntity.objects.get(slug='hard_cover')
cover_attr = ProductAttribute.objects.get(code='cover')

attr_codes = ('additional', 'editors', 'year', 
        'page_count', 'translation', 'subtitle')

def main(books):
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
            newbook, created = Product.objects.get_or_create(upc=upc,
                        title=book['title'],
                        authors=book.get('authors',''),
                        description=book.get('annotation', ''),
                        slug=book['slug'],
                        defaults = dict(
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
                if 'cover' in book:
                    if book['cover'].upper() == u'ПЕРЕПЛЕТ':
                        value = hard_cover 
                    else:
                        value = soft_cover
                    cover_record = ProductAttributeValue(
                            attribute = cover_attr,
                            product = newbook,
                            value = value)
                    cover_record.save()
                if 'cover_file' in book:
                    try:
                        with open(get_cover_file(book['cover_file']), 'rb') as f:
                            ProductImage(
                                    product = newbook,
                                    original = File(f),
                                    display_order = 0
                                    ).save()
                    except IOError: pass

