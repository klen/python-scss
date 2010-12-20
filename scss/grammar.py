from pyparsing import Word, Suppress, Literal, alphanums, hexnums, nums, SkipTo, oneOf, ZeroOrMore, Optional, OneOrMore, Forward, cStyleComment, Combine


# Base css word and literals
IDENT = NAME = Word(alphanums + "_-")
NUMBER = Word(nums+'-', nums + '.')
COMMA, COLON, SEMICOLON = [Suppress(c) for c in ",:;"]
LACC, RACC, LPAREN, RPAREN, LBRACK, RBRACK = [Suppress(c) for c in "{}()[]"]

# Comment
COMMENT = cStyleComment

# Directives
CDO = Literal("<!--")
CDC = Literal("-->")
INCLUDES = "~="
DASHMATCH = "|="
IMPORT_SYM = Literal("@import")
PAGE_SYM = Literal("@page")
MEDIA_SYM = Literal("@media")
FONT_FACE_SYM = Literal("@font-face")
CHARSET_SYM = Literal("@charset")

# SCSS directives
MIXIN_SYM = Suppress("@mixin")
INCLUDE_SYM = Suppress("@include")
EXTEND_SYM = Suppress("@extend")

# SCSS Variables
MATH_OPERATOR = oneOf("+ - / *")
VARIABLE = "$" + IDENT
VAR_STRING = VARIABLE + ZeroOrMore(MATH_OPERATOR + (VARIABLE | NUMBER))
DEC_VAR = Suppress("#") + LACC + VARIABLE + RACC

# Property values
HASH = Word('#', alphanums + "_-")
HEXCOLOR = Literal("#") + Word(hexnums, min=3, max=6)
EMS = NUMBER + Literal("em")
EXS = NUMBER + Literal("ex")
LENGTH = NUMBER + oneOf("px cm mm in pt pc")
ANGLE = NUMBER + oneOf("deg rad grad")
TIME = NUMBER + oneOf("ms s")
FREQ = NUMBER + oneOf("Hz kHz")
DIMEN = NUMBER + IDENT
PERCENTAGE = NUMBER + Literal("%")
URI = Literal("url(") + SkipTo(")")("path") + Literal(")")
FUNCTION = IDENT + Literal("(") + SkipTo(")") + Literal(")")
PRIO = "!important"

# Operators
OPERATOR = oneOf("/ ,")
COMBINATOR = oneOf("+ >")
UNARY_OPERATOR = oneOf("- +")

# SCSS parent reference
PARENT_REFERENCE = Literal("&")

# Simple selectors
ELEMENT_NAME = IDENT | Literal("*") | PARENT_REFERENCE
CLASS = Word('.', alphanums + "-_")
ATTRIB = LBRACK + SkipTo("]") + RBRACK
PSEUDO = Word(':', alphanums + "-_")

# Selectors
SELECTOR_FILTER = HASH | CLASS | ATTRIB | PSEUDO
SELECTOR = Combine(ELEMENT_NAME + SELECTOR_FILTER) | ELEMENT_NAME | SELECTOR_FILTER
SELECTOR_GROUP = SELECTOR + ZeroOrMore(Optional(COMBINATOR) + SELECTOR)
SELECTOR_TREE = SELECTOR_GROUP + ZeroOrMore(COMMA + SELECTOR_GROUP)

# Property values
TERM = Optional(UNARY_OPERATOR) + (( LENGTH | PERCENTAGE
            | FREQ | EMS | EXS | ANGLE | TIME | NUMBER
        ) | FUNCTION | URI | IDENT | HEXCOLOR | VAR_STRING)
EXPR = TERM + ZeroOrMore(Optional(OPERATOR) + TERM) + Optional(PRIO)
DEC_NAME = OneOrMore(NAME | DEC_VAR)
DECLARATION = DEC_NAME + COLON + EXPR + Optional(SEMICOLON)

# SCSS group of declarations
DECLARESET = Forward()
DECLARESET << IDENT + COLON + LACC + OneOrMore(DECLARESET | DECLARATION) + RACC

# SCSS include
INCLUDE_PARAMS = LPAREN + TERM + ZeroOrMore(COMMA + TERM) + RPAREN
INCLUDE = INCLUDE_SYM + IDENT + Optional(INCLUDE_PARAMS) + SEMICOLON

# SCSS extend
EXTEND = EXTEND_SYM + SELECTOR + SEMICOLON

# SCSS variable assigment
VARIABLE_ASSIGMENT = Suppress("$") + IDENT + COLON + TERM + SEMICOLON

# Ruleset
RULESET = Forward()
RULESET << (
    SELECTOR_TREE +
    LACC + ZeroOrMore(
        COMMENT |
        VARIABLE_ASSIGMENT |
        EXTEND |
        DECLARESET |
        DECLARATION |
        INCLUDE |
        RULESET)
    + RACC )

# SCSS mixin
MIXIN_PARAM = VARIABLE + Optional(COLON + TERM)
MIXIN_PARAMS = LPAREN + MIXIN_PARAM + ZeroOrMore(COMMA + MIXIN_PARAM) + RPAREN

MIXIN = (MIXIN_SYM + IDENT + Optional(MIXIN_PARAMS) +
    LACC + ZeroOrMore(
        COMMENT |
        VARIABLE_ASSIGMENT |
        DECLARESET |
        DECLARATION |
        INCLUDE |
        RULESET)
    + RACC)

# Root elements
IMPORT = IMPORT_SYM + URI + Optional(IDENT + ZeroOrMore(IDENT)) + SEMICOLON
MEDIA = MEDIA_SYM + IDENT + ZeroOrMore(COMMA + IDENT) + LACC + ZeroOrMore( VARIABLE_ASSIGMENT | RULESET | MIXIN ) + RACC
FONT_FACE = FONT_FACE_SYM + LACC + DECLARATION + ZeroOrMore(SEMICOLON + DECLARATION) + RACC
PSEUDO_PAGE = ":" + IDENT
PAGE = PAGE_SYM + Optional(IDENT) + Optional(PSEUDO_PAGE) + LACC + DECLARATION + ZeroOrMore(SEMICOLON + DECLARATION) + RACC
CHARSET = CHARSET_SYM + IDENT + SEMICOLON

# Css stylesheet
STYLESHEET = (
        Optional(CHARSET) +
        ZeroOrMore(CDC | CDO) +
        ZeroOrMore(IMPORT + Optional(ZeroOrMore(CDC | CDO))) +
        ZeroOrMore(
            ( VARIABLE_ASSIGMENT | MIXIN | RULESET | MEDIA | PAGE | FONT_FACE | COMMENT ) +
            ZeroOrMore(CDC | CDO)
        )
)
