import unittest

from scss import parser


class TestSCSS( unittest.TestCase ):

    def test_font_face(self):
        src = """
            @font-face {
                    font-family: 'MyMinionPro';
                src: url('minion-webfont.eot?') format('eot'),
                    url('minion-webfont.woff') format('woff'),
                    url('minion-webfont.ttf') format('truetype');
                    font-weight: normal;
                    font-style: normal;
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
        test = "@font-face {\n\tfont-family: 'MyMinionPro';\n\tfont-style: normal;\n\tfont-weight: normal;\n\tsrc: url('minion-webfont.eot?') format('eot'), url('minion-webfont.woff') format('woff'), url('minion-webfont.ttf') format('truetype')}\n\n@font-face {\n\tfont-family: 'MyMinionProItalic';\n\tfont-style: italic;\n\tfont-weight: normal;\n\tsrc: url('minionpro-it-webfont.eot?') format('eot'), url('minionpro-it-webfont.woff') format('woff'), url('minionpro-it-webfont.ttf') format('truetype')}\n\nh1, h2, h3, time, ol#using .number {\n\tfont-family: 'MyMinionPro';\n\tfont-weight: normal}"
        out = parser.parse(src)
        self.assertEqual(test, out)

