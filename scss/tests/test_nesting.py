import unittest

from scss.parser import Stylesheet


class TestSCSS( unittest.TestCase ):

    def setUp(self):
        self.parser = Stylesheet()

    def test_variables(self):
        src = """
            table.hl {
                margin: 2em 0;
                td.ln {
                    text-align: right;

                    li {
                        color: red;
                    }
                    &:hover {
                        width: 20px;
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
        test = "table.hl {\n\tmargin: 2em 0}\n\ntable.hl td.ln {\n\ttext-align: right}\n\ntable.hl td.ln li {\n\tcolor: #f00}\n\ntable.hl td.ln:hover {\n\twidth: 20px}\n\nli {\n\tfont-weight: bold;\n\tfont-size: 1.2em;\n\tfont-family: serif}\n\n"
        out = self.parser.loads(src)
        self.assertEqual(test, out)

