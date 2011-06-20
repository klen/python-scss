import unittest

from scss.parser import Stylesheet


class TestSCSS( unittest.TestCase ):

    def setUp(self):
        self.parser = Stylesheet()

    def test_extend(self):
        src = """
        .error {
            border: 1px #f00;
            background-color: #fdd;
        }
        .error .intrusion {
            background-image: url("/image/hacked.png");
        }
        .seriousError {
            @extend .error;
            border-width: 3px;
        }
        """
        test = ".error, .seriousError {\n\tborder: 1px #f00;\n\tbackground-color: #fdd}\n\n.error .intrusion, .seriousError .intrusion {\n\tbackground-image: url('/image/hacked.png')}\n\n.seriousError {\n\tborder-width: 3px}\n\n"
        out = self.parser.loads(src)
        self.assertEqual(test, out)
