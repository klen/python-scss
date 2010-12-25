import os.path
import sys
import unittest

BASEDIR = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(BASEDIR))
from scss import parser

class TestSCSS( unittest.TestCase ):

    def test_base(self):
        src = """@charset utf-8;\n@import url(test);\n@mixin z-base {
                a:hover, a:active { outline: none; }
                a, a:active, a:visited { color: #607890; }
                a:hover { color: #036; }
                @debug test;
            }\n@media print {
                @include z-base; }
            // Test comment
            /* Css comment */
            body {
                $font: Georgia;
                font-family: $font, sans-serif;
                *font:13px/1.231 sans-serif; }
            .test {
            color: red;
            &:after { content: 'blue'; }}
            pre, code, kbd, samp {
                font: 12px/10px;
                font-family: monospace, sans-serif; }
            abbr[title], dfn[title] {
                border:2px; }
            """
        test = "@charset utf-8;\n@import url(test);\n@media print { \na:hover, a:active {\n\toutline: none}\n\na, a:active, a:visited {\n\tcolor: #607890}\n\na:hover {\n\tcolor: #036}\n }/* Css comment */ \n\nbody {\n\t*font: 13px/1.231 sans-serif;\n\tfont-family: Georgia,sans-serif}\n\n.test {\n\tcolor: red}\n\n.test:after {\n\tcontent: 'blue'}\n\npre, code, kbd, samp {\n\tfont: 12px/10px;\n\tfont-family: monospace,sans-serif}\n\nabbr[title], dfn[title] {\n\tborder: 2px}"
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
        test = "#navbar {\n\theight: 23px;\n\twidth: 80%}\n\n#navbar ul {\n\tlist-style-type: none}\n\n#navbar li {\n\tfloat: left}\n\n#navbar li a.test .main {\n\tfont-weight: bold}"
        out = parser.parse(src)
        self.assertEqual(test, out)

    def test_nestproperties(self):
        src = """.fakeshadow {
            border: {
                style: solid;
                left: { width: 4px; color: #888; }
                right: { width: 2px; color: #ccc; }
            } }"""
        test = ".fakeshadow {\n\tborder-left-color: #888;\n\tborder-left-width: 4px;\n\tborder-right-color: #ccc;\n\tborder-right-width: 2px;\n\tborder-style: solid}"
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
        test = "div.rounded-top p {\n\t-moz-border-radius-top: 10px;\n\t-webkit-border-top-radius: 10px;\n\tborder-top-radius: 10px}"
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
        test = "#navbar li {\n\t-moz-border-radius-top: 10px;\n\t-webkit-border-top-radius: 10px;\n\tborder-top-radius: 10px}\n\n#footer {\n\t-moz-border-radius-top: 5px;\n\t-webkit-border-top-radius: 5px;\n\tborder-top-radius: 5px}\n\n#sidebar {\n\t-moz-border-radius-left: 8px;\n\t-webkit-border-left-radius: 8px;\n\tborder-left-radius: 8px}"
        out = parser.parse(src)
        self.assertEqual(test, out)

    def test_extend_rule(self):
        src = """.error { border: 1px #f00; background-color: #fdd; }
            a:hover {text-decoration: underline}
            .hoverlink {@extend a:hover}
            .error .intrusion { background-image: url(/image/hacked.png); }
            .seriousError { @extend .error; border-width: 3px; }"""
        test = ".error, .seriousError {\n\tbackground-color: #fdd;\n\tborder: 1px #f00}\n\na:hover, .hoverlink {\n\ttext-decoration: underline}\n\n.error .intrusion, .seriousError .intrusion {\n\tbackground-image: url(/image/hacked.png)}\n\n.seriousError {\n\tborder-width: 3px}"
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

    def test_mixin(self):
        src = """
        @mixin font {
            font: {
                weight: inherit;
                style: inherit;
                size: 100%;
                family: inherit; };
            vertical-align: baseline; }
        @mixin global { .global { border:red; @include font; }}
        @include global;
        @mixin rounded-top {
            $side: top;
            $radius: 10px;
            border-#{$side}-radius: $radius;
            -moz-border-radius-#{$side}: $radius;
            -webkit-border-#{$side}-radius: $radius; }
            #navbar li { @include rounded-top; }
            #footer { @include rounded-top; }"""
        test = ".global {\n\tborder: red;\n\tfont-family: inherit;\n\tfont-size: 100%;\n\tfont-style: inherit;\n\tfont-weight: inherit;\n\tvertical-align: baseline}\n\n#navbar li {\n\t-moz-border-radius-top: 10px;\n\t-webkit-border-top-radius: 10px;\n\tborder-top-radius: 10px}\n\n#footer {\n\t-moz-border-radius-top: 10px;\n\t-webkit-border-top-radius: 10px;\n\tborder-top-radius: 10px}"
        out = parser.parse(src)
        self.assertEqual(test, out)

    def test_for(self):
        src = """
            .test {
                $for: 4;
                color: blue;
                @for $i from 1 through $for {
                    .span-#{$i} { width: $i*40 - 10px; }
                }
            }
        """
        test = ".test {\n\tcolor: blue}\n\n.test .span-1 {\n\twidth: 30px}\n\n.test .span-2 {\n\twidth: 70px}\n\n.test .span-3 {\n\twidth: 110px}\n\n.test .span-4 {\n\twidth: 150px}"
        out = parser.parse(src)
        self.assertEqual(test, out)

    def test_operations_and_functions(self):
        src = """#navbar {
            $navbar-width: 800px;
            $items: 1 + 2;
            $navbar-color: #ce4dd6;
            width: $navbar-width;
            border-bottom: 2px solid $navbar-color;

            #{enumerate(div, 1, $items)} { color: red; }

            li { float: left;
                font: 8px/10px;
                test: 5px + (4px * (2 + $items));
                margin: 3px + 5.5px auto;
                width: $navbar-width/$items - 10px;
                background-color: $navbar-color - #333;
                &:hover { background-color: $navbar-color - 10%; } } }"""
        test = "#navbar {\n\tborder-bottom: 2px solid #ce4dd6;\n\twidth: 800px}\n\n#navbar div1, #navbar div2, #navbar div3 {\n\tcolor: red}\n\n#navbar li {\n\tbackground-color: #9b1aa3;\n\tfloat: left;\n\tfont: 8px/10px;\n\tmargin: 8.5px auto;\n\ttest: 25px;\n\twidth: 256.67px}\n\n#navbar li:hover {\n\tbackground-color: #b945c0}"
        out = parser.parse(src)
        self.assertEqual(test, out)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSCSS)
    unittest.TextTestRunner(verbosity=2).run(suite)
