import lxml
from lxml.html import HTMLParser
from lxml.html import tostring
from tidylib import tidy_fragment
import re
from os.path import expanduser, join

intersection = lxml.etree.XPath("$set1[count(.|$set2) = count($set2)]") 

patterns = (
('page_count', re.compile(r"(\d+)\s*страниц")),
('price', re.compile(r"цена.*?(\d+)\s*[руб|р\.]", re.I)),
('price_kop', re.compile(r".*?(\d+)\s+коп\.")),
('year', re.compile(r"Практика.*?(\d+)")),
('cover', re.compile(r"(Переплет|Обложка)", re.I)),
('editors', re.compile(r"(.*редактор.*)", re.I)),
('translation',   re.compile(r".*((перевод|пер\.)\s+с[ \w\.]+)", re.I)),
('absent', re.compile(r"(Временно отсутствует)", re.I)),
('issue', re.compile(r"(.*издание.*)", re.I)),
)
multiplewhite = re.compile(r"(\s)\s+")
subtitle = re.compile(r"книга\s+\d", re.I)
books_dir = expanduser("~/html/practica.ru/docs/Books")

clean = lambda line: (
        multiplewhite.sub(" ", line)
        .replace('\x95', '\u2022')  # remove &#149;
        .replace('\x97', '\u2014')  # mdash 
        .replace(' \u2022 ', '\xa0\u2022 ')  # add nbsp before bullet
        .replace('\xad', '')  # remove tab
        )

drop_a = lambda el: [a.drop_tag() for a in el.xpath("descendant::a|descendant::img")]
def remove_attr(el):
    for key in el.attrib:
        del el.attrib[key]

parser = HTMLParser(encoding='cp1251', 
        remove_blank_text=True, remove_comments = True)

def books_from_category(cat, catalog):
    a = catalog.xpath("//a[@name='{}']".format(cat['slug']))[0]  # noqa
    head_tr = a.xpath('ancestor::tr[1]')[0]

    next_head_tr = head_tr.xpath(
            "following-sibling::tr[@bgcolor='#333399'][1]")
    if len(next_head_tr) > 0:
        next_head_tr = next_head_tr[0]
        return intersection(catalog,  # noqa
            set1 = head_tr.xpath("following-sibling::tr[descendant::a]"),
            set2 = next_head_tr.xpath("preceding-sibling::tr[descendant::a]")
            ) 
    else:  # last portion
        return head_tr.xpath("following-sibling::tr[descendant::a]")

def parse_book_file(href, book):
    block = {}
    book_tree = lxml.html.parse(join(books_dir, href), parser)
    if not 'page_count' in book:
        td = book_tree.xpath(
                "//td[descendant::*[contains(text(), '{}')]]".format(
                    book['title'])
                )
        if len(td):
            td = td[0]
            page_info = td.xpath("descendant::*[contains(text(), 'страниц')]")
            if len(page_info):
                book['page_count'] = patterns[0][1].search(
                        tostring(page_info[0], encoding='unicode')).groups()[0]

    block['annotation'] = book_tree.xpath(
            r"//table[descendant::*[contains(text(), 'Аннотация')]]")
    block['contents'] = book_tree.xpath(
            r"//table[descendant::*[contains(text(), 'Содержание')]]")
    for key in block:
        if len(block[key]):
            mark = block[key][-1]
            book[key] = ""
            for element in mark.itersiblings():
                if element.tag == "table":
                    break
                drop_a(element)
                remove_attr(element)
                book[key] += tostring(element, encoding='unicode')
            book[key] = tidy_fragment(clean(book[key]))[0]
    return book

def parse_book_tr(tr):
    book = {}
    a = tr.xpath('descendant::a[descendant-or-self::*[text()]]')
    if len(a):
        a = a[0]
    else:
        return None
    book['href'] = href = a.get('href')
    if href is None:
        return None
    book['slug'] = href[:href.find(".")]
    book['title'] = clean(a.xpath("descendant-or-self::*[text()]")[0].text)
    print(book['title'])
    img = tr.xpath('descendant::img[1]')[0]
    book['cover_file'] = img.get('src')
    book['cover_width'] = img.get('width')
    book['cover_height'] = img.get('height')

    td = tr.xpath('td[3]')[0]
    book['additional'] = ""
    book['price_kop'] = 0
    book['absent'] = False
    lines_count = 0
    for line in td.itertext():
        found = False
        line = line.strip()
        if len(line):
            lines_count += 1
            if lines_count == 2:  # authors
                authors = clean(line).strip()
                if subtitle.search(authors) is not None:
                    book['subtitle'] = authors
                    lines_count -= 1
                else:
                    book['authors'] = authors
                continue
            elif lines_count == 1:
                continue  # title
            for key, regexp in patterns:
                result = regexp.search(line)
                if result is not None:
                    found = True
                    book[key] = result.groups()[0]
            if not found :
                book['additional'] += "{}\n".format(line)
    book['additional'] = clean(book['additional'].strip())
    parse_book_file(href, book)
    return book

def main(categories, catalog):
    books = []
    for cat in categories: 
        series = {'title': cat['name'],
                'slug': cat['slug'],
                'books': []}
        for book_tr in books_from_category(cat, catalog):
            book = parse_book_tr(book_tr)
            if book is not None:
                series['books'].append(book)
        books.append(series)
    return books
