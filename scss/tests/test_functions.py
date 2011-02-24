import unittest

from scss.parser import Stylecheet


class TestSCSS( unittest.TestCase ):

    def setUp(self):
        self.parser = Stylecheet()

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
                p & {
                    color: blue }
                color: red; }
            }

            li {
                background-color: $navbar-color - #333;
                float: left;
                font: 8px/10px $font;
                margin: 3px + 5.5px auto;
                height: 5px + (4px * (2 + $items));
                width: $navbar-width/$items - 10px;
                &:hover { background-color: $navbar-color - 10%; } }"""
        test = "#navbar {\n\twidth: 800px;\n\tborder-bottom: 2px solid #646437}\n\n#navbar div1, #navbar div2, #navbar div3 {\n\tcolor: red}\n\n#navbar p div1, #navbar p div2, #navbar p div3 {\n\tcolor: blue}\n\nli {\n\tfloat: left;\n\tmargin: 8.5px auto;\n\twidth: 256.667px;\n\theight: 25px;\n\tbackground-color: #313104;\n\tfont: 8px/10px 'Verdana', monospace}\n\nli:hover {\n\tbackground-color: #5c5c3e}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)

    def test_rgb_functions(self):
        src = """
            @option warn:false;

            $color: rgba(23, 45, 67, .4)
            $color2: #fdc;
            .test {
                red: red($color);
                blue: blue($color);
                green: green($color);
                color: mix(#f00, #00f, 25%);
            }
        """
        test = ".test {\n\tcolor: #3f00bf;\n\tred: 23;\n\tblue: 67;\n\tgreen: 45}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)

    def test_hsl_functions(self):
        src = """
            @option warn:false;

            $hsl: hsla(0, 100%, 25%, .4);
            .test {
                color: $hsl;
                hue: hue($hsl);
                saturation: saturation($hsl);
                background-color: adjust-hue( #811, 45deg);
            }
        """
        test = ".test {\n\tbackground-color: #886a10;\n\tcolor: rgba(127,0,0,0.40);\n\thue: 0;\n\tsaturation: 255}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)

    def test_opacity_functions(self):
        src = """
            $color: rgba(100, 100, 100, .4);
            .test {
                color: opacify( $color, 60% );
            }
        """
        test = ".test {\n\tcolor: #646464}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)

    def test_string_functions(self):
        src = """
            $top: 'top';
            $bottom: bottom;
            .test {
                bottom: quote($bottom);
                top: unquote($top);
            }
        """
        test = ".test {\n\ttop: top;\n\tbottom: 'bottom'}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)

    def test_number_functions(self):
        src = """
            @option warn:false;

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
        test = ".test {\n\ttop: 200%;\n\tround: 100.0;\n\tceil: 2.0;\n\tfloor: 1.0;\n\tabs: 1.24}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)

    def test_introspection_functions(self):
        src = """
            @option warn:false;

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

    def test_compass_helpers(self):
        src = """
            #{append-selector(".foo, .bar", ".baz")} {
                color: red;
            }

            .example {

                #{elements-of-type(block)} {
                    border: 1px solid #777777;
                    margin: 1em 3em; }

                #{elements-of-type(inline)} {
                    color: #cc0000; }
            }

            a {
                #{headings(2, 4)} {
                    font-weight: bold;
                }
            }
        """
        test = ".foo .baz, .bar .baz {\n\tcolor: red}\n\n.example address, .example article, .example aside, .example blockquote, .example center, .example dd, .example dialog, .example dir, .example div, .example dl, .example dt, .example fieldset, .example figure, .example footer, .example form, .example frameset, .example h1, .example h2, .example h3, .example h4, .example h5, .example h6, .example header, .example hgroup, .example hr, .example isindex, .example menu, .example nav, .example noframes, .example noscript, .example ol, .example p, .example pre, .example section, .example ul {\n\tmargin: 1em 3em;\n\tborder: 1px solid #777}\n\n.example a, .example abbr, .example acronym, .example b, .example basefont, .example bdo, .example big, .example br, .example cite, .example code, .example dfn, .example em, .example font, .example i, .example img, .example input, .example kbd, .example label, .example q, .example s, .example samp, .example select, .example small, .example span, .example strike, .example strong, .example sub, .example sup, .example textarea, .example tt, .example u, .example var {\n\tcolor: #c00}\n\na h2, a h3, a h4 {\n\tfont-weight: bold}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)
