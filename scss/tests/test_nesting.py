import unittest

from scss import parser


class TestSCSS( unittest.TestCase ):

    def test_variables(self):
        src = """
            table.hl {
                margin: 2em 0;
                td.ln {
                    text-align: right;

                    li {
                        color: red;
                    }
                }
            }

            li {
                font: {
                    family: serif;
                    weight: bold;
                    size: 1.2em;
                }
            }
            """
        test = "table.hl {\n\tmargin: 2em 0}\n\ntable.hl td.ln {\n\ttext-align: right}\n\ntable.hl td.ln li {\n\tcolor: red}\n\nli {\n\tfont-family: serif;\n\tfont-size: 1.2em;\n\tfont-weight: bold}"
        out = parser.parse(src)
        self.assertEqual(test, out)

