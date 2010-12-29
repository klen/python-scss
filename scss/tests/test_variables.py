import unittest

from scss import parser


class TestSCSS( unittest.TestCase ):

    def test_variables(self):
        src = """
            $blue: #3bbfce;
            $margin: 16px;

            .content-navigation {
                border-color: $blue;
                color: $blue - 9%;
            }

            .border {
                padding: $margin / 2;
                margin: $margin / 2;
                border-color: $blue;
            }
            """
        test = ".content-navigation {\n\tborder-color: #3bbfce;\n\tcolor: #35adbb}\n\n.border {\n\tborder-color: #3bbfce;\n\tmargin: 8px;\n\tpadding: 8px}"
        out = parser.parse(src)
        self.assertEqual(test, out)
