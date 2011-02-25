import os.path
import unittest

from scss.parser import Stylecheet


class TestSCSS( unittest.TestCase ):

    def test_working(self):
        path = os.path.join(os.path.dirname(__file__), 'working.scss')
        parser = Stylecheet()
        test = parser.parse(open(path).read())
        print test
