import unittest

from scss.parser import Stylesheet


class TestSCSS( unittest.TestCase ):

    def setUp(self):
        self.parser = Stylesheet(options=dict(compress=True))

    def test_math(self):
        src = """

        a.red {
            color:red
        }

        div#autoscroll_container .ui-button-text-only:not(.ui-state-active) .ui-button-text {
            // These two lines cause a blur effect.
            color: transparent;
            text-shadow: 0px 0px 4px #111111;
        }

        """
        test = ""
        out = self.parser.loads(src)
        self.assertEqual(test, out)
