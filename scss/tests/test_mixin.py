import unittest

from scss.parser import Stylesheet


class TestSCSS( unittest.TestCase ):

    def setUp(self):
        self.parser = Stylesheet()

    def test_mixin(self):
        src = """
        @mixin font {
            font: {
                weight: inherit;
                style: inherit;
                size: 100%;
                family: inherit; };
            vertical-align: baseline; }

        @mixin global {
            .global {
                border:red;
                @include font;
            }
        }

        @include global;

        @mixin rounded-top( $radius:10px ) {
            $side: top;
            border-#{$side}-radius: $radius;
            -moz-border-radius-#{$side}: $radius;
            -webkit-border-#{$side}-radius: $radius;
        }
        #navbar li { @include rounded-top; }
        #footer { @include rounded-top(5px); }
        """
        test = ".global {\n\tborder: #f00;\n\tvertical-align: baseline;\n\tfont-weight: inherit;\n\tfont-style: inherit;\n\tfont-size: 100%;\n\tfont-family: inherit}\n\n#navbar li {\n\tborder-top-radius: 10px;\n\t-moz-border-radius-top: 10px;\n\t-webkit-border-top-radius: 10px}\n\n#footer {\n\tborder-top-radius: 5px;\n\t-moz-border-radius-top: 5px;\n\t-webkit-border-top-radius: 5px}\n\n"
        out = self.parser.loads(src)
        self.assertEqual(test, out)
