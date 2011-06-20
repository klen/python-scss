import unittest

from scss.parser import Stylesheet


class TestSCSS( unittest.TestCase ):

    def setUp(self):
        self.parser = Stylesheet()

    def test_for(self):
        src = """
            @mixin test($src:2px){
                $width: $src + 5px;
                width: $width;
            }
            .test {
                color: blue;
                @for $i from 1 through 4 {
                    .span-#{$i}{
                        @include test($i); }
                }
            }
        """
        test = ".test {\n\tcolor: #00f}\n\n.test .span-1 {\n\twidth: 6px}\n\n.test .span-2 {\n\twidth: 7px}\n\n.test .span-3 {\n\twidth: 8px}\n\n.test .span-4 {\n\twidth: 9px}\n\n"
        out = self.parser.loads(src)
        self.assertEqual(test, out)
