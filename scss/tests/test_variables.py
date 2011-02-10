import unittest

from scss import parser


class TestSCSS( unittest.TestCase ):

    def test_variables(self):
        src = """
            $blue: #3bbfce !default;
            $test: rgb(120, 35, 64);
            $test2: rgba(120, 35, 64, .4);
            $margin: 16px;
            $image: 'test.png';

            .content-navigation {
                border-color: $blue;
                background-color: $test + 5%;
                background-image: url('/test/' + $image);
                color: $blue - 9%;
            }

            .border {
                padding: $margin / 2;
                margin: $margin / 2;
                padding-left: -$margin + 2px;
                border-color: $blue;
                color: $test2;
                font: -1.5em;
            }
            """
        test = ".content-navigation {\n\tbackground-color: #7e2443;\n\tbackground-image: url('/test/test.png');\n\tborder-color: #3bbfce;\n\tcolor: #35adbb}\n\n.border {\n\tborder-color: #3bbfce;\n\tcolor: rgba(120, 35, 64, .4);\n\tfont: -1.5em;\n\tmargin: 8px;\n\tpadding: 8px;\n\tpadding-left: -14px}"
        out = parser.parse(src)
        self.assertEqual(test, out)
