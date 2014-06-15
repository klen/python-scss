#!/usr/bin/env python

""" Python SCSS parser. """

import operator

from . import compat


VERSION_INFO = (0, 8, 73)

__project__ = "scss"
__version__ = "0.8.73"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "GNU LGPL"


CONV = {
    'size': {
        'em': 13.0,
        'px': 1.0},
    'length': {
        'mm': 1.0,
        'cm': 10.0,
        'in': 25.4,
        'pt': 25.4 / 72,
        'pc': 25.4 / 6},
    'time': {
        'ms': 1.0,
        's': 1000.0},
    'freq': {
        'hz': 1.0,
        'khz': 1000.0},
    'any': {
        '%': 1.0 / 100,
        'deg': 1.0 / 360,
        's': 1.0 / 60}}
CONV_TYPE = {}
CONV_FACTOR = {}
for t, m in CONV.items():
    for k, f in m.items():
        CONV_TYPE[k] = t
        CONV_FACTOR[k] = f

OPRT = {
    '^': operator.__pow__,
    '+': operator.__add__,
    '-': operator.__sub__,
    '*': operator.__mul__,
    '/': compat.div,
    '!': operator.__neg__,
    '<': operator.__lt__,
    '<=': operator.__le__,
    '>': operator.__gt__,
    '>=': operator.__ge__,
    '==': operator.__eq__,
    '=': operator.__eq__,
    '!=': operator.__ne__,
    '&': operator.__and__,
    '|': operator.__or__,
    'and': lambda x, y: x and y,
    'or': lambda x, y: x or y,
}

ELEMENTS_OF_TYPE = {
    'block': (
        "address, article, aside, blockquote, center, dd, dialog, dir, div, dl, dt, fieldset, "
        "figure, footer, form, frameset, h1, h2, h3, h4, h5, h6, header, hgroup, hr, isindex, "
        "menu, nav, noframes, noscript, ol, p, pre, section, ul"),
    'inline': (
        "a, abbr, acronym, b, basefont, bdo, big, br, cite, code, dfn, em, font, i, img, input, "
        "kbd, label, q, s, samp, select, small, span, strike, strong, sub, sup, textarea, tt, u, "
        "var"),
    'table': 'table', 'list-item': 'li', 'table-row-group': 'tbody',
    'table-header-group': 'thead', 'table-footer-group': 'tfoot', 'table-row':
    'tr', 'table-cell': 'td, th', }

COLORS = {
    'aliceblue': '#f0f8ff',
    'antiquewhite': '#faebd7',
    'aqua': '#00ffff',
    'aquamarine': '#7fffd4',
    'azure': '#f0ffff',
    'beige': '#f5f5dc',
    'bisque': '#ffe4c4',
    'black': '#000000',
    'blanchedalmond': '#ffebcd',
    'blue': '#0000ff',
    'blueviolet': '#8a2be2',
    'brown': '#a52a2a',
    'burlywood': '#deb887',
    'cadetblue': '#5f9ea0',
    'chartreuse': '#7fff00',
    'chocolate': '#d2691e',
    'coral': '#ff7f50',
    'cornflowerblue': '#6495ed',
    'cornsilk': '#fff8dc',
    'crimson': '#dc143c',
    'cyan': '#00ffff',
    'darkblue': '#00008b',
    'darkcyan': '#008b8b',
    'darkgoldenrod': '#b8860b',
    'darkgray': '#a9a9a9',
    'darkgreen': '#006400',
    'darkkhaki': '#bdb76b',
    'darkmagenta': '#8b008b',
    'darkolivegreen': '#556b2f',
    'darkorange': '#ff8c00',
    'darkorchid': '#9932cc',
    'darkred': '#8b0000',
    'darksalmon': '#e9967a',
    'darkseagreen': '#8fbc8f',
    'darkslateblue': '#483d8b',
    'darkslategray': '#2f4f4f',
    'darkturquoise': '#00ced1',
    'darkviolet': '#9400d3',
    'deeppink': '#ff1493',
    'deepskyblue': '#00bfff',
    'dimgray': '#696969',
    'dodgerblue': '#1e90ff',
    'firebrick': '#b22222',
    'floralwhite': '#fffaf0',
    'forestgreen': '#228b22',
    'fuchsia': '#ff00ff',
    'gainsboro': '#dcdcdc',
    'ghostwhite': '#f8f8ff',
    'gold': '#ffd700',
    'goldenrod': '#daa520',
    'gray': '#808080',
    'green': '#008000',
    'greenyellow': '#adff2f',
    'honeydew': '#f0fff0',
    'hotpink': '#ff69b4',
    'indianred': '#cd5c5c',
    'indigo': '#4b0082',
    'ivory': '#fffff0',
    'khaki': '#f0e68c',
    'lavender': '#e6e6fa',
    'lavenderblush': '#fff0f5',
    'lawngreen': '#7cfc00',
    'lemonchiffon': '#fffacd',
    'lightblue': '#add8e6',
    'lightcoral': '#f08080',
    'lightcyan': '#e0ffff',
    'lightgoldenrodyellow': '#fafad2',
    'lightgreen': '#90ee90',
    'lightgrey': '#d3d3d3',
    'lightpink': '#ffb6c1',
    'lightsalmon': '#ffa07a',
    'lightseagreen': '#20b2aa',
    'lightskyblue': '#87cefa',
    'lightslategray': '#778899',
    'lightsteelblue': '#b0c4de',
    'lightyellow': '#ffffe0',
    'lime': '#00ff00',
    'limegreen': '#32cd32',
    'linen': '#faf0e6',
    'magenta': '#ff00ff',
    'maroon': '#800000',
    'mediumaquamarine': '#66cdaa',
    'mediumblue': '#0000cd',
    'mediumorchid': '#ba55d3',
    'mediumpurple': '#9370db',
    'mediumseagreen': '#3cb371',
    'mediumslateblue': '#7b68ee',
    'mediumspringgreen': '#00fa9a',
    'mediumturquoise': '#48d1cc',
    'mediumvioletred': '#c71585',
    'midnightblue': '#191970',
    'mintcream': '#f5fffa',
    'mistyrose': '#ffe4e1',
    'moccasin': '#ffe4b5',
    'navajowhite': '#ffdead',
    'navy': '#000080',
    'oldlace': '#fdf5e6',
    'olive': '#808000',
    'olivedrab': '#6b8e23',
    'orange': '#ffa500',
    'orangered': '#ff4500',
    'orchid': '#da70d6',
    'palegoldenrod': '#eee8aa',
    'palegreen': '#98fb98',
    'paleturquoise': '#afeeee',
    'palevioletred': '#db7093',
    'papayawhip': '#ffefd5',
    'peachpuff': '#ffdab9',
    'peru': '#cd853f',
    'pink': '#ffc0cb',
    'plum': '#dda0dd',
    'powderblue': '#b0e0e6',
    'purple': '#800080',
    'red': '#ff0000',
    'rosybrown': '#bc8f8f',
    'royalblue': '#4169e1',
    'saddlebrown': '#8b4513',
    'salmon': '#fa8072',
    'sandybrown': '#f4a460',
    'seagreen': '#2e8b57',
    'seashell': '#fff5ee',
    'sienna': '#a0522d',
    'silver': '#c0c0c0',
    'skyblue': '#87ceeb',
    'slateblue': '#6a5acd',
    'slategray': '#708090',
    'snow': '#fffafa',
    'springgreen': '#00ff7f',
    'steelblue': '#4682b4',
    'tan': '#d2b48c',
    'teal': '#008080',
    'thistle': '#d8bfd8',
    'tomato': '#ff6347',
    'turquoise': '#40e0d0',
    'violet': '#ee82ee',
    'wheat': '#f5deb3',
    'white': '#ffffff',
    'whitesmoke': '#f5f5f5',
    'yellow': '#ffff00',
    'yellowgreen': '#9acd32'
}

SORTING = dict((v, k) for k, v in enumerate((

    # Positioning
    'position',
    'top',
    'right',
    'bottom',
    'left',
    'z-index',

    # Box behavior and properties
    'float',
    'clear',
    'display',
    'visibility',
    'overflow',
    'overflow-x',
    'overflow-y',
    'overflow-style',
    'zoom',
    'clip',
    'box-sizing',
    'box-shadow',

    # Sizing
    'margin',
    'margin-top',
    'margin-right',
    'margin-bottom',
    'margin-left',
    'padding',
    'padding-top',
    'padding-right',
    'padding-bottom',
    'padding-left',
    'width',
    'height',
    'max-width',
    'max-height',
    'min-width',
    'min-height',

    # Color appearance
    'outline',
    'outline-offset',
    'outline-width',
    'outline-style',
    'outline-color',
    'border',
    'border-break',
    'border-collapse',
    'border-color',
    'border-image',
    'border-top-image',
    'border-right-image',
    'border-bottom-image',
    'border-left-image',
    'border-corner-image',
    'border-top-left-image',
    'border-top-right-image',
    'border-bottom-right-image',
    'border-bottom-left-image',
    'border-fit',
    'border-length',
    'border-spacing',
    'border-style',
    'border-width',
    'border-top',
    'border-top-width',
    'border-top-style',
    'border-top-color',
    'border-right',
    'border-right-width',
    'border-right-style',
    'border-right-color',
    'border-bottom',
    'border-bottom-width',
    'border-bottom-style',
    'border-bottom-color',
    'border-left',
    'border-left-width',
    'border-left-style',
    'border-left-color',
    'border-radius',
    'border-top-right-radius',
    'border-top-left-radius',
    'border-bottom-right-radius',
    'border-bottom-left-radius',
    'background',
    'filter:progid:DXImageTransform.Microsoft.AlphaImageLoader',
    'background-color',
    'background-image',
    'background-repeat',
    'background-attachment',
    'background-position',
    'background-position-x',
    'background-position-y',
    'background-break',
    'background-clip',
    'background-origin',
    'background-size',
    'color',

    # Special content types
    'table-layout',
    'caption-side',
    'empty-cells',
    'list-style',
    'list-style-position',
    'list-style-type',
    'list-style-image',
    'quotes',
    'content',
    'counter-increment',
    'counter-reset',

    # Text
    'direction',
    'vertical-align',
    'text-align',
    'text-align-last',
    'text-decoration',
    'text-emphasis',
    'text-height',
    'text-indent',
    'text-justify',
    'text-outline',
    'text-replace',
    'text-transform',
    'text-wrap',
    'text-shadow',
    'line-height',
    'white-space',
    'white-space-collapse',
    'word-break',
    'word-spacing',
    'word-wrap',
    'letter-spacing',
    'font',
    'font-weight',
    'font-style',
    'font-variant',
    'font-size',
    'font-size-adjust',
    'font-family',
    'font-effect',
    'font-emphasize',
    'font-emphasize-position',
    'font-emphasize-style',
    'font-smooth',
    'font-stretch',
    'src',

    # Visual properties
    'opacity',
    'filter:progid:DXImageTransform.Microsoft.Alpha',
    '-ms-filter:progid:DXImageTransform.Microsoft.Alpha',
    'transitions',
    'resize',
    'cursor',

    # Print
    'page-break-before',
    'page-break-inside',
    'page-break-after',
    'orphans',
    'widows',

    # Transfom
    'transition',
    'transition-delay',
    'transition-duration',
    'transition-property',
    'transition-timing-function',

)))


class ScssException(Exception):

    """ Raise SCSS exception. """

    pass
