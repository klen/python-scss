import unittest

from scss.parser import Stylecheet


class TestSCSS( unittest.TestCase ):

    def setUp(self):
        self.parser = Stylecheet()

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
        test = "table.hl {\n\tmargin: 2em 0}\n\ntable.hl td.ln {\n\ttext-align: right}\n\ntable.hl td.ln li {\n\tcolor: red}\n\nli {\n\tfont-weight: bold;\n\tfont-size: 1.2em;\n\tfont-family: serif}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)

