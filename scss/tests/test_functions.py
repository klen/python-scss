import unittest

from scss import parser


class TestSCSS( unittest.TestCase ):

    def test_operations_and_functions(self):
        src = """
        #navbar {
            $navbar-width: 800px;
            $items: 1 + 2;
            $navbar-color: rgb(12, 44, 55);
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
        test = "#navbar {\n\tborder-bottom: 2px solid #0c2c37;\n\twidth: 800px}\n\n#navbar div1, #navbar div2, #navbar div3 {\n\tcolor: red}\n\n#navbar * html div1, #navbar * html div2, #navbar * html div3 {\n\tcolor: blue}\n\nli {\n\tbackground-color: #000004;\n\tfloat: left;\n\tfont: 8px/10px 'Verdana', monospace;\n\tmargin: 8.5px auto;\n\ttest: 25px;\n\twidth: 256.667px}\n\nli:hover {\n\tbackground-color: #0a2731}"
        out = parser.parse(src)
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
        out = parser.parse(src)
        self.assertEqual(test, out)

