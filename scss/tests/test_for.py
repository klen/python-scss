import unittest

from scss.parser import Stylecheet


class TestSCSS( unittest.TestCase ):

    def setUp(self):
        self.parser = Stylecheet()

    def test_for(self):
        src = """
            @mixin test($src:2px){
                $width: $src + 5px;
                width: $width;
            }
            $test: 9px;
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
        out = self.parser.parse(src)
        self.assertEqual(test, out)
