import unittest

from scss import parser


class TestSCSS( unittest.TestCase ):

    def test_variables(self):
        src = """
            $blue: #ffdd00 !default;
            $test: rgb(120, 35, 64);
            $test2: rgba(120, 35, 64, .4);
            $margin: 16px;
            $side: top;
            $image: 'test.png';

            .content-navigation {
                border-color: $blue;
                background-color: $test + 5%;
                background-image: url('/test/' + $image);
                color: $blue - 9%;
                margin: 0 ( -$margin * 2 ) 12px;
            }

            .border {
                padding-#{$side}: $margin / 2;
                margin: $margin / 2;
                padding-left: -$margin + 2px;
                border-#{$side}: {
                    color:  $blue;
                }
                color: $test2;
                font: -1.5em;
            }
            """
        test = ".content-navigation {\n\tbackground-color: #7e2443;\n\tbackground-image: url('/test/test.png');\n\tborder-color: #fd0;\n\tcolor: #e8e800;\n\tmargin: 0 -32px 12px}\n\n.border {\n\tborder-top-color: #fd0;\n\tcolor: rgba(120,35,64,0.40);\n\tfont: -1.5em;\n\tmargin: 8px;\n\tpadding-left: -14px;\n\tpadding-top: 8px}"
        out = parser.parse(src)
        self.assertEqual(test, out)
