#!/usr/bin/env python
import operator


VERSION_INFO = (0, 5, 2)

__project__ = PROJECT = __name__
__version__ = VERSION = '.'.join(str(i) for i in VERSION_INFO)
__author__ = AUTHOR = "Kirill Klenov <horneds@gmail.com>"
__license__ = LICENSE = "GNU LGPL"


CONV = {
    'size': {
        'em': 13.0,
        'px': 1.0
    },
    'length': {
        'mm':  1.0,
        'cm':  10.0,
        'in':  25.4,
        'pt':  25.4 / 72,
        'pc':  25.4 / 6
    },
    'time': {
        'ms':  1.0,
        's':   1000.0
    },
    'freq': {
        'hz':  1.0,
        'khz': 1000.0
    },
    'any': {
        '%': 1.0 / 100,
        'deg': 1.0 / 360
    }
}
CONV_TYPE = {}
CONV_FACTOR = {}
for t, m in CONV.items():
    for k, f in m.items():
        CONV_TYPE[k] = t
        CONV_FACTOR[k] = f
del t, m, k, f

OPRT = {
    '^' : operator.__pow__,
    '+' : operator.__add__,
    '-' : operator.__sub__,
    '*' : operator.__mul__,
    '/' : operator.__div__,
    '!' : operator.__neg__,
    '<' : operator.__lt__,
    '<=': operator.__le__,
    '>' : operator.__gt__,
    '>=': operator.__ge__,
    '==': operator.__eq__,
    '=' : operator.__eq__,
    '!=': operator.__ne__,
}

ELEMENTS_OF_TYPE = {
    'block': 'address, article, aside, blockquote, center, dd, dialog, dir, div, dl, dt, fieldset, figure, footer, form, frameset, h1, h2, h3, h4, h5, h6, header, hgroup, hr, isindex, menu, nav, noframes, noscript, ol, p, pre, section, ul',
    'inline': 'a, abbr, acronym, b, basefont, bdo, big, br, cite, code, dfn, em, font, i, img, input, kbd, label, q, s, samp, select, small, span, strike, strong, sub, sup, textarea, tt, u, var',
    'table': 'table',
    'list-item': 'li',
    'table-row-group': 'tbody',
    'table-header-group': 'thead',
    'table-footer-group': 'tfoot',
    'table-row': 'tr',
    'table-cell': 'td, th',
}
