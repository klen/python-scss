from pyparsing import Word, Suppress, Literal, alphanums, hexnums, nums, SkipTo, oneOf, ZeroOrMore, Optional, OneOrMore, Forward, cStyleComment, Combine, dblSlashComment


# Base css word and literals
IDENT = NAME = Word(alphanums + "_-")
NUMBER = Word(nums+'-', nums + '.')
COMMA, COLON, SEMICOLON = [Literal(c) for c in ",:;"]
LACC, RACC, LPAREN, RPAREN, LBRACK, RBRACK = [Suppress(c) for c in "{}()[]"]
LLACC, LRACC = [Literal(c) for c in "{}"]

# Comment
CSS_COMMENT = cStyleComment
SCSS_COMMENT = dblSlashComment
COMMENT = CSS_COMMENT | SCSS_COMMENT

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
IF_SYM = Suppress("@if")
ELSE_SYM = Suppress("@else")

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
PRIO = "!important"

# SCSS Variables
VARIABLE = "$" + IDENT

# Operators
MATH_OPERATOR = oneOf("+ - / *")
OPERATOR = oneOf("/ ,")
COMBINATOR = oneOf("+ >")
UNARY_OPERATOR = oneOf("- +")
IF_OPERATOR = oneOf("== != <= >= < >")

# Parse values
FUNCTION = IDENT + LPAREN + SkipTo(")") + RPAREN
SIMPLE_VALUE = LENGTH | PERCENTAGE | FREQ | EMS | EXS | ANGLE | TIME | NUMBER | FUNCTION | IDENT | HEXCOLOR
VALUE = SIMPLE_VALUE | VARIABLE
SIMPLE_STRING = Combine(SIMPLE_VALUE + OneOrMore(Optional(OPERATOR) + SIMPLE_VALUE))
VAL_STRING = VALUE + ZeroOrMore(MATH_OPERATOR + VALUE)
INTERPOLATION_VAR = Suppress("#") + LACC + VAL_STRING + RACC

# Property values
# TERM = Optional(UNARY_OPERATOR.suppress()) + (URI | VAL_STRING)
# EXPR = TERM + ZeroOrMore(Optional(OPERATOR) + TERM) + Optional(PRIO)
EXPR = OneOrMore(SIMPLE_STRING | VAL_STRING | URI) + Optional(PRIO)
DEC_NAME = OneOrMore(NAME | INTERPOLATION_VAR)
DECLARATION = DEC_NAME + COLON + EXPR + Optional(SEMICOLON.suppress())

# SCSS group of declarations
DECLARESET = Forward()
DECLARESET << IDENT + COLON.suppress() + LACC + OneOrMore(DECLARESET | DECLARATION) + RACC

# SCSS parent reference
PARENT_REFERENCE = Literal("&")

# Selectors
ELEMENT_NAME = Combine(OneOrMore(IDENT | PARENT_REFERENCE)) | Literal("*")
CLASS = Word('.', alphanums + "-_")
ATTRIB = LBRACK + SkipTo("]") + RBRACK
PSEUDO = Word(':', alphanums + "-_")
SEL_NAME = ELEMENT_NAME + Optional(INTERPOLATION_VAR)

# TODO: Bug this
FILTER = HASH | CLASS | ATTRIB | PSEUDO
SEL_FILTER = FILTER + Optional(INTERPOLATION_VAR)
SELECTOR = (SEL_NAME + SEL_FILTER) | INTERPOLATION_VAR | SEL_NAME | SEL_FILTER

# SELECTOR = INTERPOLATION_VAR | ELEMENT_NAME | FILTER
# SELECTOR.skipWhitespace = False

SELECTOR_GROUP = SELECTOR + ZeroOrMore(Optional(COMBINATOR) + SELECTOR)
SELECTOR_TREE = SELECTOR_GROUP + ZeroOrMore(COMMA.suppress() + SELECTOR_GROUP)

# SCSS include
INCLUDE_PARAMS = LPAREN + VAL_STRING + ZeroOrMore(COMMA.suppress() + VAL_STRING) + RPAREN
INCLUDE = INCLUDE_SYM + IDENT + Optional(INCLUDE_PARAMS) + Optional(SEMICOLON.suppress())

# SCSS extend
EXTEND = EXTEND_SYM + SELECTOR + Optional(SEMICOLON.suppress())

# SCSS variable assigment
VAR_DEFAULT = "!default"
VARIABLE_ASSIGMENT = Suppress("$") + IDENT + COLON.suppress() + VAL_STRING + Optional(VAR_DEFAULT) + Optional(SEMICOLON.suppress())

# Ruleset
RULESET = Forward()
BASE_CONTENT = COMMENT | DECLARESET | DECLARATION | INCLUDE | RULESET | VARIABLE_ASSIGMENT

# SCSS control directives
IF_CONDITION = VALUE + Optional(IF_OPERATOR + VALUE)
IF_BODY = LACC + ZeroOrMore(BASE_CONTENT) + RACC
ELSE = ELSE_SYM + LACC + ZeroOrMore(BASE_CONTENT) + RACC
IF = IF_SYM + IF_CONDITION + IF_BODY + Optional(ELSE)

RULESET << (
    SELECTOR_TREE +
    LACC + ZeroOrMore(BASE_CONTENT | IF | EXTEND) + RACC )

# SCSS mixin
MIXIN_PARAM = VARIABLE + Optional(COLON.suppress() + VAL_STRING)
MIXIN_PARAMS = LPAREN + MIXIN_PARAM + ZeroOrMore(COMMA.suppress() + MIXIN_PARAM) + RPAREN
MIXIN = (MIXIN_SYM + IDENT + Optional(MIXIN_PARAMS) +
    LACC + ZeroOrMore(BASE_CONTENT | IF) + RACC)

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
