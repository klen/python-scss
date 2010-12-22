import os.path
import sys
import unittest

BASEDIR = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(BASEDIR))
from scss import parser

class TestSCSS( unittest.TestCase ):

    def test_nesting_1(self):
        src = ".test { color: red; a p { color: blue; }}"
        test = ".test {\n\tcolor: red}\n\n.test a p {\n\tcolor: blue}"
        out = parser.parse(src)
        self.assertEqual(test, out)

    def test_nesting_2(self):
        src = """#navbar {
          width: 80%;
          height: 23px;
          ul { list-style-type: none; }
          li { float: left;
            a .test .main{ font-weight: bold; }
          } }"""
        test = "#navbar {\n\twidth: 80%;\n\theight: 23px}\n\n#navbar ul {\n\tlist-style-type: none}\n\n#navbar li {\n\tfloat: left}\n\n#navbar li a.test .main {\n\tfont-weight: bold}"
        out = parser.parse(src)
        self.assertEqual(test, out)

    def test_nestproperties(self):
        src = """.fakeshadow {
            border: {
                style: solid;
                left: { width: 4px; color: #888; }
                right: { width: 2px; color: #ccc; }
            } }"""
        test = ".fakeshadow {\n\tborder-style: solid;\n\tborder-left-width: 4px;\n\tborder-left-color: #888;\n\tborder-right-width: 2px;\n\tborder-right-color: #ccc}"
        out = parser.parse(src)
        self.assertEqual(test, out)

    def test_parent_references(self):
        src = """a { color: #ce4dd6;
            &:hover { color: #ffb3ff; }
            &:visited { color: #c458cb; }
            .test & { color: red; }}"""
        test = "a {\n\tcolor: #ce4dd6}\n\na:hover {\n\tcolor: #ffb3ff}\n\na:visited {\n\tcolor: #c458cb}\n\n.test a {\n\tcolor: red}"
        out = parser.parse(src)
        self.assertEqual(test, out)

    def test_variables(self):
        src = """$main-color: #ce4dd6;
            $style: solid;
            $def_test: first;
            $def_test: second;
            $def_test: beep-beep !default;
            #navbar { border-bottom: { color: $main-color; style: $style; } }
            a.#{$def_test} { color: $main-color; &:hover { border-bottom: $style 1px; } }"""
        test = "#navbar {\n\tborder-bottom-color: #ce4dd6;\n\tborder-bottom-style: solid}\n\na.second {\n\tcolor: #ce4dd6}\n\na.second:hover {\n\tborder-bottom: solid 1px}"
        out = parser.parse(src)
        self.assertEqual(test, out)

    def test_interpolation(self):
        src = """$side: top;
            $radius: 10px;
            div.rounded-#{$side} p {
            border-#{$side}-radius: $radius;
            -moz-border-radius-#{$side}: $radius;
            -webkit-border-#{$side}-radius: $radius; }"""
        test = "div.rounded-top p {\n\tborder-top-radius: 10px;\n\t-moz-border-radius-top: 10px;\n\t-webkit-border-top-radius: 10px}"
        out = parser.parse(src)
        self.assertEqual(test, out)

    def test_mixin(self):
        src = """@mixin rounded-top {
            $side: top;
            $radius: 10px;
            border-#{$side}-radius: $radius;
            -moz-border-radius-#{$side}: $radius;
            -webkit-border-#{$side}-radius: $radius; }
            #navbar li { @include rounded-top; }
            #footer { @include rounded-top; }"""
        test = "#navbar li {\n\tborder-top-radius: 10px;\n\t-moz-border-radius-top: 10px;\n\t-webkit-border-top-radius: 10px}\n\n#footer {\n\tborder-top-radius: 10px;\n\t-moz-border-radius-top: 10px;\n\t-webkit-border-top-radius: 10px}"
        out = parser.parse(src)
        self.assertEqual(test, out)

    def test_mixin_arg(self):
        src = """@mixin rounded($side, $radius: 10px) {
            border-#{$side}-radius: $radius;
            -moz-border-radius-#{$side}: $radius;
            -webkit-border-#{$side}-radius: $radius; }
            #navbar li { @include rounded(top); }
            #footer { @include rounded(top, 5px); }
            #sidebar { @include rounded(left, 8px); }"""
        test = "#navbar li {\n\tborder-top-radius: 10px;\n\t-moz-border-radius-top: 10px;\n\t-webkit-border-top-radius: 10px}\n\n#footer {\n\tborder-top-radius: 5px;\n\t-moz-border-radius-top: 5px;\n\t-webkit-border-top-radius: 5px}\n\n#sidebar {\n\tborder-left-radius: 8px;\n\t-moz-border-radius-left: 8px;\n\t-webkit-border-left-radius: 8px}"
        out = parser.parse(src)
        self.assertEqual(test, out)

    def test_extend_rule(self):
        src = """.error { border: 1px #f00; background-color: #fdd; }
            a:hover {text-decoration: underline}
            .hoverlink {@extend a:hover}
            .error .intrusion { background-image: url(/image/hacked.png); }
            .seriousError { @extend .error; border-width: 3px; }"""
        test = ".error, .seriousError {\n\tborder: 1px #f00;\n\tbackground-color: #fdd}\n\na:hover, .hoverlink {\n\ttext-decoration: underline}\n\n.error .intrusion, .seriousError .intrusion {\n\tbackground-image: url(/image/hacked.png)}\n\n.seriousError {\n\tborder-width: 3px}"
        out = parser.parse(src)
        self.assertEqual(test, out)

    def test_if(self):
        src = """$type: monster; $test: 11;
            @if $test { .test { border: 2px; } }
            @mixin test($fix: 0) {
                @if $fix { display: block; } @else { display: none; }
            }
            span { @include test(false) }
            p { border: red;
                @if $type == monster { color: blue;
                    b { color: red; }
                } @else { color: black; } } """
        test = ".test {\n\tborder: 2px}\n\nspan {\n\tdisplay: none}\n\np {\n\tborder: red;\n\tcolor: blue}\n\np b {\n\tcolor: red}"
        out = parser.parse(src)
        self.assertEqual(test, out)

    def test_for(self):
        src = """
            .test {
                $for: 3;
                color: blue;
                @for $i from 1 through $for {
                    .span#{$i} { border: red; }
                }
            }
        """
        test = ".test {\n\tcolor: blue}\n\n.test .span1 {\n\tborder: red}\n\n.test .span2 {\n\tborder: red}"
        out = parser.parse(src)
        self.assertEqual(test, out)

    def test_operations_and_functions(self):
        src = """#navbar {
            $navbar-width: 800px;
            $items: 3 + 2;
            $navbar-color: #ce4dd6;
            width: $navbar-width;
            border-bottom: 2px solid $navbar-color;

            #{enumerate(div, 1, $items)} { color: red; }

            li { float: left;
                font: 8px/10px;
                test: 5px + 4px * (2 + $items);
                margin: 3px + 5px auto;
                width: $navbar-width/$items - 10px;
                background-color: $navbar-color - #333;
                &:hover { background-color: $navbar-color - 10%; } } }"""
        test = "#navbar {\n\twidth: 800px;\n\tborder-bottom: 2px solid #ce4dd6}\n\n#navbar div1, div2, div3, div4 {\n\tcolor: red}\n\n#navbar li {\n\tfloat: left;\n\tfont: 8px/10px;\n\ttest: 63px;\n\tmargin: 8px auto;\n\twidth: 150px;\n\tbackground-color: #9b1aa3}\n\n#navbar li:hover {\n\tbackground-color: #b945c0}"
        out = parser.parse(src)
        self.assertEqual(test, out)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSCSS)
    unittest.TextTestRunner(verbosity=2).run(suite)
