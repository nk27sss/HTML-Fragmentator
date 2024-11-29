import re
import unittest
import tests.funcs_t as funcs

from split_msg import split_message, FragmentatorException


### unit-тесты.
class TestSplitMessage(unittest.TestCase):
    
    def test_split_microdemo150(self):
        source = "tests/data/microdemo150.html"
        max_len = 150
        gen = split_message(source, max_len)
        fragments = list(gen)
        funcs.assert_universal_base_format_fragments(self, fragments, max_len)

    def test_split_source4096(self):
        source = "tests/data/source.html"
        max_len = 4096
        gen = split_message(source, max_len)
        fragments = list(gen)
        funcs.assert_universal_base_format_fragments(self, fragments, max_len)

    def test_split_source4396(self):
        source = "tests/data/source.html"
        max_len = 4396
        gen = split_message(source, max_len)
        fragments = list(gen)
        funcs.assert_universal_base_format_fragments(self, fragments, max_len)
    
    def test_split_source3000(self):
        source = "tests/data/source.html"
        max_len = 3000
        gen = split_message(source, max_len)
        fragments = list(gen)
        funcs.assert_universal_base_format_fragments(self, fragments, max_len)

    def test_split_impossible(self):
        source = "tests/data/impossible.html"
        max_len = 150
        try:
            gen = split_message(source, max_len)
            fragments = list(gen)
        except FragmentatorException as e:
            return
        self.assertTrue(False, msg="Ошибки не возникло!")
            

if __name__ == '__main__':
    unittest.main()
