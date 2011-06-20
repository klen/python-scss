import unittest

from scss.parser import Stylesheet


class TestSCSS( unittest.TestCase ):

    def setUp(self):
        self.parser = Stylesheet()

    def test_font_face(self):
        src = """
            @font-face {
                    font-family: 'MyMinionPro';
                src: url('minion-webfont.eot?') format('eot'),
                    url('minion-webfont.woff') format('woff'),
                    url('minion-webfont.ttf') format('truetype');
                    font-weight: normal;
                    font-style: normal;
                    font-size: ( 12px / 16px ) * 100%;
            }

            @font-face {
                    font-family: 'MyMinionProItalic';
                src: url('minionpro-it-webfont.eot?') format('eot'),
                    url('minionpro-it-webfont.woff') format('woff'),
                    url('minionpro-it-webfont.ttf') format('truetype');
                    font-weight: normal;
                    font-style: italic;
            }

            h1,h2,h3, time, ol#using .number {
                    font-weight: normal;
                    font-family: 'MyMinionPro';
            }
        """
        test = "@font-face {\n\tfont-weight: normal;\n\tfont-style: normal;\n\tfont-size: 75%;\n\tfont-family: 'MyMinionPro';\n\tsrc: url('minion-webfont.eot?') format('eot') , url('minion-webfont.woff') format('woff') , url('minion-webfont.ttf') format('truetype')}\n\n@font-face {\n\tfont-weight: normal;\n\tfont-style: italic;\n\tfont-family: 'MyMinionProItalic';\n\tsrc: url('minionpro-it-webfont.eot?') format('eot') , url('minionpro-it-webfont.woff') format('woff') , url('minionpro-it-webfont.ttf') format('truetype')}\n\nh1, h2, h3, time, ol#using .number {\n\tfont-weight: normal;\n\tfont-family: 'MyMinionPro'}\n\n"
        out = self.parser.loads(src)
        self.assertEqual(test, out)
