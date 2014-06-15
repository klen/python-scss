import os
import unittest

from scss import parser


class ScssCache(unittest.TestCase):

    path = os.path.join(os.path.dirname(__file__), 'example.scss')
    cache_path = os.path.join(os.path.dirname(__file__), 'example.ccss')

    def tearDown(self):
        os.remove(self.cache_path)

    def test_cache(self):
        src = open(self.path).read()
        test = parser.parse(src)
        file = open(self.path)
        out = parser.load(file, precache=True)
        self.assertEqual(test, out)
        cached_out = parser.load(file, precache=True)
        self.assertEqual(test, cached_out)