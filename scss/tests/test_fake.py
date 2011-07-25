import unittest

from scss.parser import Stylesheet


class TestSCSS( unittest.TestCase ):

    def setUp(self):
        self.parser = Stylesheet(options=dict(compress=True))

    def test_math(self):
        src = """
            .bug {
                background: -webkit-gradient(linear, top left, 100% 100%, from(#ddd), to(#aaa));
            }

        """
        test = ""
        out = self.parser.loads(src)
        self.assertEqual(test, out)
