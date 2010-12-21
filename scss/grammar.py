from pyparsing import Word, Suppress, Literal, alphanums, hexnums, nums, SkipTo, oneOf, ZeroOrMore, Optional, OneOrMore, Forward, cStyleComment, Combine


# Base css word and literals
IDENT = NAME = Word(alphanums + "_-")
NUMBER = Word(nums+'-', nums + '.')
COMMA, COLON, SEMICOLON = [Literal(c) for c in ",:;"]
LACC, RACC, LPAREN, RPAREN, LBRACK, RBRACK = [Suppress(c) for c in "{}()[]"]
LLACC, LRACC = [Literal(c) for c in "{}"]

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

# SCSS Variables
VARIABLE = "$" + IDENT
DEC_VAR = Suppress("#") + LACC + VARIABLE + RACC

# Operators
MATH_OPERATOR = oneOf("+ - / *")
OPERATOR = oneOf("/ ,")
COMBINATOR = oneOf("+ >")
UNARY_OPERATOR = oneOf("- +")

VALUE = LENGTH | PERCENTAGE | FREQ | EMS | EXS | ANGLE | TIME | NUMBER | FUNCTION | IDENT | HEXCOLOR | VARIABLE
VAL_STRING = VALUE + ZeroOrMore(MATH_OPERATOR + VALUE)

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
SELECTOR_TREE = SELECTOR_GROUP + ZeroOrMore(COMMA.suppress() + SELECTOR_GROUP)

# Property values
TERM = Optional(UNARY_OPERATOR.suppress()) + (URI | VAL_STRING)
EXPR = TERM + ZeroOrMore(Optional(OPERATOR) + TERM) + Optional(PRIO)
DEC_NAME = OneOrMore(NAME | DEC_VAR)
DECLARATION = DEC_NAME + COLON + EXPR + Optional(SEMICOLON.suppress())

# SCSS group of declarations
DECLARESET = Forward()
DECLARESET << IDENT + COLON.suppress() + LACC + OneOrMore(DECLARESET | DECLARATION) + RACC

# SCSS include
INCLUDE_PARAMS = LPAREN + VAL_STRING + ZeroOrMore(COMMA.suppress() + VAL_STRING) + RPAREN
INCLUDE = INCLUDE_SYM + IDENT + Optional(INCLUDE_PARAMS) + SEMICOLON.suppress()

# SCSS extend
EXTEND = EXTEND_SYM + SELECTOR + SEMICOLON.suppress()

# SCSS variable assigment
VARIABLE_ASSIGMENT = Suppress("$") + IDENT + COLON.suppress() + VAL_STRING + SEMICOLON.suppress()

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
MIXIN_PARAM = VARIABLE + Optional(COLON.suppress() + VAL_STRING)
MIXIN_PARAMS = LPAREN + MIXIN_PARAM + ZeroOrMore(COMMA.suppress() + MIXIN_PARAM) + RPAREN

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
MEDIA = MEDIA_SYM + IDENT + ZeroOrMore(COMMA + IDENT) + LLACC + ZeroOrMore( VARIABLE_ASSIGMENT | RULESET | MIXIN ) + LRACC
FONT_FACE = FONT_FACE_SYM + LLACC + DECLARATION + ZeroOrMore(SEMICOLON + DECLARATION) + LRACC
PSEUDO_PAGE = ":" + IDENT
PAGE = PAGE_SYM + Optional(IDENT) + Optional(PSEUDO_PAGE) + LLACC + DECLARATION + ZeroOrMore(SEMICOLON + DECLARATION) + LRACC
CHARSET = CHARSET_SYM + IDENT + SEMICOLON

# Css stylesheet
STYLESHEET = ZeroOrMore(
    CDC | CDO
    | COMMENT
    | CHARSET
    | VARIABLE_ASSIGMENT
    | MIXIN
    | RULESET
    | MEDIA
    | PAGE
    | FONT_FACE
)
