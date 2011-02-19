import unittest

from scss.parser import Stylecheet


class TestSCSS( unittest.TestCase ):

    parser = Stylecheet()

    def test_operations_and_functions(self):
        src = """
        #navbar {
            $navbar-width: 800px;
            $items: 1 + 2;
            $navbar-color: rgb(100, 100, 55);
            $font: "Verdana", monospace;
            width: $navbar-width;
            border-bottom: 2px solid $navbar-color;

            #{enumerate("div", 1, $items)} {
                * html & {
                    color: blue }
                color: red; }
            }

            li {
                background-color: $navbar-color - #333;
                float: left;
                font: 8px/10px $font;
                margin: 3px + 5.5px auto;
                test: 5px + (4px * (2 + $items));
                width: $navbar-width/$items - 10px;
                &:hover { background-color: $navbar-color - 10%; } }"""
        test = "#navbar {\n\tborder-bottom: 2px solid #646437;\n\twidth: 800px}\n\n#navbar div1, #navbar div2, #navbar div3 {\n\tcolor: red}\n\n#navbar * html div1, #navbar * html div2, #navbar * html div3 {\n\tcolor: blue}\n\nli {\n\tbackground-color: #313104;\n\tfloat: left;\n\tfont: 8px/10px 'Verdana', monospace;\n\tmargin: 8.5px auto;\n\ttest: 25px;\n\twidth: 256.667px}\n\nli:hover {\n\tbackground-color: #5c5c3e}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)

    def test_rgb_functions(self):
        src = """
            $color: rgba(23, 45, 67, .4)
            $color2: #fdc;
            .test {
                red: red($color);
                blue: blue($color);
                green: green($color);
                mix: mix(#f00, #00f, 25%);
            }
        """
        test = ".test {\n\tblue: 67;\n\tgreen: 45;\n\tmix: #3f00bf;\n\tred: 23}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)

    def test_hsl_functions(self):
        src = """
            $hsl: hsla(0, 100%, 25%, .4);
            .test {
                hsl: $hsl;
                hue: hue($hsl);
                saturation: saturation($hsl);
                adj: adjust-hue( #811, 45deg);
            }
        """
        test = ".test {\n\tadj: #886a10;\n\thsl: #7f0000;\n\thue: 0;\n\tsaturation: 255}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)

    def test_opacity_functions(self):
        src = """
            $color: rgba(100, 100, 100, .4);
            .test {
                opacify: opacify( $color, 60% );
            }
        """
        test = ".test {\n\topacify: #646464}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)

    def test_string_functions(self):
        src = """
            $top: 'top';
            $bottom: bottom;
            .test {
                top: unquote($top);
                bottom: quote($bottom);
            }
        """
        test = ".test {\n\tbottom: 'bottom';\n\ttop: top}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)

    def test_number_functions(self):
        src = """
            $top: 100px;
            $bottom: 50px;
            .test {
                top: percentage($top / $bottom);
                round: round($top);
                ceil: ceil(1.24);
                floor: floor(1.24);
                abs: abs(-1.24);
            }
        """
        test = ".test {\n\tabs: 1.24;\n\tceil: 2.0;\n\tfloor: 1.0;\n\tround: 100.0;\n\ttop: 200%}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)

    def test_introspection_functions(self):
        src = """
            $top: 100px;
            $color: #f00;
            .test {
                test: type-of($top);
                test2: type-of($color);
                test3: unit($top);
                test4: unitless($top);
            }
        """
        test = ".test {\n\ttest: number;\n\ttest2: color;\n\ttest3: px;\n\ttest4: false}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)
