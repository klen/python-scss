import unittest

from scss.parser import Stylesheet


class TestSCSS( unittest.TestCase ):

    def setUp(self):
        self.parser = Stylesheet()

    def test_base(self):
        src = """
            @charset utf-8;
            @import url(test);

            @warn "Test warnings!"
            @mixin z-base {
                a:hover, a:active { outline: none; }
                a, a:active, a:visited { color: #607890; }
                a:hover { color: #036; }
                @debug test; }

            @media print { @include z-base; }

            // Test comment
            /* Css comment */
            body {
                $font: Georgia;

                margin-bottom: .5em;
                font-family: $font, sans-serif;
                *font:13px/1.231 sans-serif; }

            ::selection {
                color: red;
            }

            .test:hover {
                color: red;
                &:after {
                    content: 'blue'; }}

            pre, code, kbd, samp {
                font: 12px/10px;
                font-family: monospace, sans-serif; }

            abbr[title], dfn[title] {
                border:2px; }

            """
        test = "@charset utf-8;\n@import url(test);\n@media print { a:hover, a:active {\n\toutline: none}\n\na, a:active, a:visited {\n\tcolor: #607890}\n\na:hover {\n\tcolor: #036}\n\n }/* Css comment */\nbody {\n\tmargin-bottom: .5em;\n\tfont-family: Georgia , sans-serif;\n\t*font: 13px / 1.231 sans-serif}\n\n::selection {\n\tcolor: #f00}\n\n.test:hover {\n\tcolor: #f00}\n\n.test:hover:after {\n\tcontent: #00f}\n\npre, code, kbd, samp {\n\tfont: 12px / 10px;\n\tfont-family: monospace , sans-serif}\n\nabbr[title], dfn[title] {\n\tborder: 2px}\n\n"
        out = self.parser.loads(src)
        self.assertEqual(test, out)

    def test_nesting_2(self):
        src = """#navbar {
          width: 80%;
          height: 23px;
          ul { list-style-type: none; }
          li { float: left;
            a .test .main{ font-weight: bold; }
          } }"""
        test = "#navbar {\n\twidth: 80%;\n\theight: 23px}\n\n#navbar ul {\n\tlist-style-type: none}\n\n#navbar li {\n\tfloat: left}\n\n#navbar li a .test .main {\n\tfont-weight: bold}\n\n"
        out = self.parser.loads(src)
        self.assertEqual(test, out)

    def test_nestproperties(self):
        src = """.fakeshadow {
            border: {
                style: solid;
                left: { width: 4px; color: #888; }
                right: { width: 2px; color: #ccc; }
            } }"""
        test = ".fakeshadow {\n\tborder-style: solid;\n\tborder-right-width: 2px;\n\tborder-right-color: #ccc;\n\tborder-left-width: 4px;\n\tborder-left-color: #888}\n\n"
        out = self.parser.loads(src)
        self.assertEqual(test, out)

    def test_parent_references(self):
        src = """a { color: #ce4dd6;
            &:hover { color: #ffb3ff; }
            &:visited { color: #c458cb; }
            .test & { color: red; }}"""
        test = "a {\n\tcolor: #ce4dd6}\n\na:hover {\n\tcolor: #ffb3ff}\n\na:visited {\n\tcolor: #c458cb}\n\n.test a {\n\tcolor: #f00}\n\n"
        out = self.parser.loads(src)
        self.assertEqual(test, out)

    def test_variables(self):
        src = """$main-color: #ce4dd6;
            $style: solid;
            $def_test: first;
            $def_test: second;
            $def_test: beep-beep !default;
            #navbar { border-bottom: { color: $main-color; style: $style; } }
            a.#{$def_test} { color: $main-color; &:hover { border-bottom: $style 1px; } }"""
        test = "#navbar {\n\tborder-bottom-style: solid;\n\tborder-bottom-color: #ce4dd6}\n\na.second {\n\tcolor: #ce4dd6}\n\na.second:hover {\n\tborder-bottom: solid 1px}\n\n"
        out = self.parser.loads(src)
        self.assertEqual(test, out)

    def test_interpolation(self):
        src = """$side: top;
            $radius: 10px;
            div.rounded-#{$side} p {
            border-#{$side}-radius: $radius;
            -moz-border-radius-#{$side}: $radius;
            -webkit-border-#{$side}-radius: $radius; }"""
        test = "div.rounded-top p {\n\tborder-top-radius: 10px;\n\t-moz-border-radius-top: 10px;\n\t-webkit-border-top-radius: 10px}\n\n"
        out = self.parser.loads(src)
        self.assertEqual(test, out)

    def test_mixin_arg(self):
        src = """@mixin rounded($side, $radius: 10px, $dummy: false) {
            border-#{$side}-radius: $radius;
            -moz-border-radius-#{$side}: $radius;
            -webkit-border-#{$side}-radius: $radius; }
            #navbar li { @include rounded(top); }
            #footer { @include rounded(top, 5px); }
            #sidebar { @include rounded(left, 8px); }"""
        test = "#navbar li {\n\tborder-top-radius: 10px;\n\t-moz-border-radius-top: 10px;\n\t-webkit-border-top-radius: 10px}\n\n#footer {\n\tborder-top-radius: 5px;\n\t-moz-border-radius-top: 5px;\n\t-webkit-border-top-radius: 5px}\n\n#sidebar {\n\tborder-left-radius: 8px;\n\t-moz-border-radius-left: 8px;\n\t-webkit-border-left-radius: 8px}\n\n"
        out = self.parser.loads(src)
        self.assertEqual(test, out)

    def test_extend_rule(self):
        src = """
            .error { border: 1px #f00; background-color: #fdd; }
            a:hover {text-decoration: underline}
            .hoverlink {@extend a:hover}
            .error .intrusion { background-image: url(/image/hacked.png); }
            .seriousError { @extend .error; border-width: 3px; }
            """
        test = ".error, .seriousError {\n\tborder: 1px #f00;\n\tbackground-color: #fdd}\n\na:hover {\n\ttext-decoration: underline}\n\n.error .intrusion, .seriousError .intrusion {\n\tbackground-image: url(/image/hacked.png)}\n\n.seriousError {\n\tborder-width: 3px}\n\n"
        out = self.parser.loads(src)
        self.assertEqual(test, out)
