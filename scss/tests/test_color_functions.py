import unittest

from scss.parser import Stylesheet


def verify_testcases(func):
    """Runs the output of the function through SCSS and compares output.

    To use: Write a function that returns a list of tuples, where the first
    element of the tuple is SCSS code and the second element the expected
    output. When you place this decorator around your function it will take the
    SCSS code, run the parser over it and assert the output equals the expected
    output."""

    def assert_testcases(self, *args, **kwargs):
        for (testcase, expected_output) in func(self, *args, **kwargs):
            out = self.parser.loads(testcase)
            self.assertEqual(expected_output, out)
    return assert_testcases


class TestSCSS(unittest.TestCase):

    """Test color functions

    """

    def setUp(self):
        self.parser = Stylesheet(options=dict(compress=True))

    @verify_testcases
    def test_invert(self):
        return [
            ('invert(#000)', '#fff'),
            ('invert(#fff)', '#000'),
            ('invert(#567)', '#a98'),
            ('invert(invert(#123456))', '#123456'),
            ('invert(rgba(100, 110, 120, 0.7))', 'rgba(155,145,135,0.70)'),
            ('invert(hsla(0, 50%, 50%, 0.7))', 'rgba(63,191,191,0.70)'),
        ]

    @verify_testcases
    def test_adjust_lightness(self):
        # First example is taken from
        # http://sass-lang.com/docs/yardoc/Sass/Script/Functions.html
        return [
            ('adjust-lightness(#800, 20%)', '#e00'),
        ]
