import re
from html.parser import HTMLParser
import unittest

# мини парсер для проверки фрагментов
def html_parser_tags(html):
    class HTMLFragmentParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.open_tags = []
            self.texts = []
            self.close_tags = []

        def handle_starttag(self, tag, attrs):
            attrs_str = ' '.join(f'{key}={value!r}' for key, value in attrs)
            self.open_tags.append(f'<{tag}{' ' + attrs_str if attrs else ''}>')

        def handle_endtag(self, tag):
            self.close_tags.append(f'</{tag}>')

        def handle_data(self, data):
            da = data.strip()
            self.texts.append(da)
                
    parser = HTMLFragmentParser()
    parser.feed(html)
    return parser.open_tags, parser.texts, parser.close_tags


def assert_universal_base_format_fragments(aself:unittest.TestCase, fragments, max_len):
    """ Проверка базового формата фрагментов """
    aself.assertIsNotNone(fragments)
    aself.assertTrue(all(type(x)==str for x in fragments))
    aself.assertTrue(all(len(x)>3 for x in fragments))
    aself.assertTrue(all(len(x)<=max_len for x in fragments))

    for frag in fragments:
        aself.assertTrue(len(frag)>0, msg=f"frag is empty:")
        open_tags, texts, close_tags = html_parser_tags(frag)
        aself.assertTrue(len(texts)+len(open_tags)+len(close_tags)>0, msg=f"frag: `{frag}`")
        aself.assertEqual(len(open_tags), len(close_tags), msg=f"open_tags!=close_tags")

    return True