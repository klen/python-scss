import unittest

from scss.parser import Stylecheet


class TestSCSS( unittest.TestCase ):

    def setUp(self):
        self.parser = Stylecheet()

    def test_operations_and_functions(self):
        src = """
            $type: monster;
             $test: 9px;

            @if $test + 2 > 10 {
                .test { border: 2px; }
            }

            @mixin test($fix: true) {
                @if $fix {
                    display: block;
                } @else {
                    display: none;
                }
            }
            span {
                @include test(false)
            }
            p {
                @if $type == girl {
                    color: pink;
                }
                @else if $type == monster {
                    color: red;
                    b { border: 2px; }
                }
                @else {
                    color: blue;
                }
            }
        """
        test = ".test {\n\tborder: 2px}\n\nspan {\n\tdisplay: none}\n\np {\n\tcolor: red}\n\np b {\n\tborder: 2px}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)
