import unittest

from scss.parser import Stylesheet


class TestSCSS( unittest.TestCase ):

    def setUp(self):
        self.parser = Stylesheet(options=dict(compress=True))

    def test_math(self):
        src = """

        $link-color:         #06c                  !default;
        $link-hover-color:   #09f                  !default;
        $link-focus-color:   $link-hover-color     !default;
        $link-active-color:  lighten(adjust-hue($link-color, 75deg), 10%) !default;
        $link-visited-color: darken($link-color, 10%) !default;

        @mixin link-colors(
            $normal,
            $hover: false,
            $active: false,
            $visited: false,
            $focus: false) {

            color: $normal;

            @if $visited {
                &:visited {
                    color: $visited; } }

            @if $focus {
                &:focus {
                    color: $focus; } }

            @if $hover {
                &:hover {
                    color: $hover; } }

            @if $active {
                &:active {
                    color: $active; } }
        }

        a {
            @include link-colors($link-color, $link-hover-color, $link-active-color, $link-visited-color, $link-focus-color);
        }

        """
        test = "960px"
        out = self.parser.loads(src)
        self.assertEqual(test, out)
