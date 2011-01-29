import unittest

from scss import parser


class TestSCSS( unittest.TestCase ):

    def test_for(self):
        src = """
            @mixin test($src:2px){
                $width: $src + 5px;
                width: $width;
            }
            $test: 9;
            $for: $test - 5;
            .test {
                color: blue;
                @for $i from 1 through $for {
                    .span-#{$i}{
                        @include test($i); }
                }
            }
        """
        test = ".test {\n\tcolor: blue}\n\n.test .span-1 {\n\twidth: 6px}\n\n.test .span-2 {\n\twidth: 7px}\n\n.test .span-3 {\n\twidth: 8px}\n\n.test .span-4 {\n\twidth: 9px}"
        out = parser.parse(src)
        self.assertEqual(test, out)
