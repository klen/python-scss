import unittest

from scss.parser import Stylecheet


class TestSCSS( unittest.TestCase ):

    def setUp(self):
        self.parser = Stylecheet()

    def test_default(self):
        src = """
        @option compress:false;
        #navbar {
            height: 100px;
            color: #ff0033;
            border: 2px solid magenta;

            li {
                background-color: red - #333;
                float: left;
                font: 8px/10px verdana;
                margin: 3px + 5.5px auto;
                height: 5px + (4px * 2);
            }
        }
        """
        test = "#navbar {\n\theight: 100px;\n\tborder: 2px solid magenta;\n\tcolor: #f03}\n\n#navbar li {\n\tfloat: left;\n\tmargin: 8.5px auto;\n\theight: 13px;\n\tbackground-color: #c00;\n\tfont: 8px/10px verdana}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)

    def test_compress(self):
        src = """
        @option compress:true;
        #navbar, p {
            height: 100px;
            color: #ff0033;
            border: 2px solid magenta;

            li {
                background-color: red - #333;
                float: left;
                font: 8px/10px verdana;
                margin: 3px + 5.5px auto;
                height: 5px + (4px * 2);
            }
        }
        """
        test = "#navbar, p {height:100px;border:2px solid magenta;color:#f03}\n#navbar li, p li {float:left;margin:8.5px auto;height:13px;background-color:#c00;font:8px/10px verdana}"
        out = self.parser.parse(src)
        self.assertEqual(test, out)
