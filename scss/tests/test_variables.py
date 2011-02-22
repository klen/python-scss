import unittest

from scss.parser import Stylecheet


class TestSCSS( unittest.TestCase ):

    def setUp(self):
        self.parser = Stylecheet()

    def test_variables(self):
        src = """
            @vars {
                $blue: #ffdd00 !default;
                $test: rgb(120, 35, 64);
                $test2: rgba(120, 35, 64, .4);
                $len: 0px or 5px;
            }
            $margin: 16px;
            $side: top;
            $image: 'test.png';

            .content-navigation {
                border-color: $blue;
                background-color: $test + 5%;
                background-image: url('/test/' + $image);
                color: $blue - 9%;
                margin: $len ( -$margin * 2 ) 12px;
            }

            .border {
                padding-#{$side}: $margin / 2;
                margin: $margin / 2;
                padding-left: -$margin + 2px;
                border-#{$side}: {
                    color:  $blue;
                }
                color: $test2;
                font: -1.5em + 50px;
            }
            """
        test = ".content-navigation {\n\tmargin: 5px -32px 12px;\n\tborder-color: #fd0;\n\tbackground-color: #7b1f3e;\n\tbackground-image: url('/test/test.png');\n\tcolor: #f3d40b}\n\n.border {\n\tmargin: 8px;\n\tpadding-top: 8px;\n\tpadding-left: -14px;\n\tborder-top-color: #fd0;\n\tcolor: rgba(120,35,64,0.40);\n\tfont: 2.346em}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)
