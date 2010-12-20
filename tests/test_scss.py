import unittest
import os.path
import sys

BASEDIR = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(BASEDIR))
from scss import parser

class TestSCSS( unittest.TestCase ):

    def testparse( self ):
        src = open(os.path.join(BASEDIR, 'test.scss')).read()
        out = parser.parse(src)
        print out


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSCSS)
    unittest.TextTestRunner(verbosity=2).run(suite)
