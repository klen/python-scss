from pyparsing import Word, Suppress, Literal, alphanums, hexnums, nums, SkipTo, oneOf, ZeroOrMore, Optional, OneOrMore, Forward, cStyleComment, Combine, dblSlashComment, quotedString, Regex, Empty, lineEnd, alphas


# Base css word and literals
EMPTY = Empty()
IDENT = NAME = Word(alphas + '_-', alphanums + "_-")
NUMBER = Combine(Optional("-") + Word(nums+'.'))
COMMA, COLON, SEMICOLON = [Literal(c) for c in ",:;"]
OPT_SEMICOLON = Optional(SEMICOLON.suppress())
LACC, RACC, LPAREN, RPAREN = [Suppress(c) for c in "{}()"]
LLACC, LRACC, LBRACK, RBRACK = [Literal(c) for c in "{}[]"]

# Comment
CSS_COMMENT = cStyleComment + Optional(lineEnd)
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
FOR_SYM = Suppress("@for")
DEBUG_SYM = Suppress("@debug")

# Property values
HASH = Word('#', alphanums + "_-")
HEXCOLOR = Suppress("#") + Word(hexnums, min=3, max=8)
NUMBER_VALUE = NUMBER + oneOf("em ex px cm mm in pt pc deg %")
PATH = Word(alphanums + "_-/.", alphanums + "_-./?#&")
PRIO = "!important"

# SCSS Variables
VARIABLE = "$" + IDENT

# Operators
MATH_OPERATOR = oneOf("+ - / *")
COMBINATOR = oneOf("+ >")
UNARY_OPERATOR = oneOf("- +")
IF_OPERATOR = oneOf("== != <= >= < >")

# Parse values
VAL_STRING = Forward()
FUNCTION = IDENT + LPAREN + VAL_STRING + ZeroOrMore(COMMA.suppress() + VAL_STRING) + RPAREN
SIMPLE_VALUE = FUNCTION | NUMBER_VALUE | NUMBER | PATH | IDENT | HEXCOLOR | quotedString
VALUE = Optional('-') + ( SIMPLE_VALUE | VARIABLE )
DIV_STRING = SIMPLE_VALUE + OneOrMore(Literal("/") + SIMPLE_VALUE)


PARENS = LPAREN + VAL_STRING + RPAREN
VAL_STRING << ((VALUE | PARENS) + ZeroOrMore(MATH_OPERATOR + ( VALUE | PARENS )))

INTERPOLATION_VAR = Suppress("#") + LACC + VAL_STRING + RACC

# Property values
SEP_VAL_STRING = VAL_STRING + OneOrMore(COMMA.suppress() + VAL_STRING)
TERM = ( DIV_STRING | VAL_STRING ) + Optional(COMMA)
EXPR = OneOrMore(TERM) + Optional(PRIO)
DEC_NAME = Optional("*") + OneOrMore(NAME | INTERPOLATION_VAR)
DECLARATION = DEC_NAME + COLON + EXPR + OPT_SEMICOLON

# SCSS group of declarations
DECLARESET = Forward()
DECLARESET << DEC_NAME + COLON.suppress() + LACC + OneOrMore(DECLARESET | DECLARATION | COMMENT) + RACC + OPT_SEMICOLON

# SCSS parent reference
PARENT_REFERENCE = Literal("&")

# Selectors
ELEMENT_NAME = Combine(OneOrMore(IDENT | PARENT_REFERENCE)) | Literal("*")
ATTRIB = LBRACK + SkipTo("]") + RBRACK
CLASS_NAME = Word('.', alphanums + "-_")
PSEUDO = Regex(r':{1,2}[A-Za-z0-9-_]+')

# TODO: Bug this
FILTER = HASH | CLASS_NAME | ATTRIB
SEL_NAME = ELEMENT_NAME + Optional(INTERPOLATION_VAR) + Optional(PSEUDO)
SEL_FILTER = FILTER + Optional(INTERPOLATION_VAR) + Optional(PSEUDO)
SELECTOR = (SEL_NAME + SEL_FILTER) | INTERPOLATION_VAR | SEL_NAME | SEL_FILTER | PSEUDO

SELECTOR_GROUP = SELECTOR + ZeroOrMore(Optional(COMBINATOR) + SELECTOR)
SELECTOR_TREE = SELECTOR_GROUP + ZeroOrMore(COMMA.suppress() + SELECTOR_GROUP)

# SCSS include
INCLUDE_PARAMS = LPAREN + VAL_STRING + ZeroOrMore(COMMA.suppress() + VAL_STRING) + RPAREN
INCLUDE = INCLUDE_SYM + IDENT + Optional(INCLUDE_PARAMS) + OPT_SEMICOLON

# SCSS extend
EXTEND = EXTEND_SYM + SELECTOR + OPT_SEMICOLON

# SCSS variable assigment
VAR_DEFAULT = "!default"
VAR_DEFINITION = Suppress("$") + IDENT + COLON.suppress() + (SEP_VAL_STRING | VAL_STRING ) + (VAR_DEFAULT | EMPTY) + OPT_SEMICOLON

# Ruleset
RULESET = Forward()
CONTENT = COMMENT | INCLUDE | VAR_DEFINITION | RULESET
RULE_CONTENT = CONTENT | DECLARESET | DECLARATION

# SCSS control directives
IF_CONDITION = VALUE + Optional(IF_OPERATOR + VALUE)
IF_BODY = LACC + ZeroOrMore(RULE_CONTENT) + RACC
ELSE = ELSE_SYM + LACC + ZeroOrMore(RULE_CONTENT) + RACC
IF = IF_SYM + IF_CONDITION + IF_BODY + (ELSE | EMPTY)
FOR_BODY = ZeroOrMore(RULE_CONTENT)
FOR = FOR_SYM + VARIABLE + Suppress("from") + VALUE + (Suppress("through") | Suppress("to")) + VALUE + LACC + FOR_BODY + RACC
DEBUG = DEBUG_SYM + VAL_STRING + OPT_SEMICOLON
CONTROL_DIR = IF | FOR | DEBUG

RULESET << (
    SELECTOR_TREE +
    LACC + ZeroOrMore(RULE_CONTENT | CONTROL_DIR | EXTEND) + RACC )

# SCSS mixin
MIXIN_PARAM = VARIABLE + Optional(COLON.suppress() + VAL_STRING)
MIXIN_PARAMS = LPAREN + MIXIN_PARAM + ZeroOrMore(COMMA.suppress() + MIXIN_PARAM) + RPAREN
MIXIN = (MIXIN_SYM + IDENT + Optional(MIXIN_PARAMS) +
    LACC + ZeroOrMore(RULE_CONTENT | CONTROL_DIR) + RACC)

# Root elements
IMPORT = IMPORT_SYM + FUNCTION + OPT_SEMICOLON
MEDIA = MEDIA_SYM + IDENT + ZeroOrMore(COMMA + IDENT) + LLACC + ZeroOrMore( RULE_CONTENT | MIXIN | CONTROL_DIR ) + LRACC
FONT_FACE = FONT_FACE_SYM + LLACC + ZeroOrMore(DECLARATION) + LRACC
VARIABLES = ( Literal("@variables") | Literal('@vars') ) + LLACC + ZeroOrMore(VAR_DEFINITION) + RACC
PSEUDO_PAGE = ":" + IDENT
PAGE = PAGE_SYM + Optional(IDENT) + Optional(PSEUDO_PAGE) + LLACC + ZeroOrMore(DECLARATION) + LRACC
CHARSET = CHARSET_SYM + IDENT + OPT_SEMICOLON

# Css stylesheet
STYLESHEET = ZeroOrMore(
    CDC | CDO
    | FONT_FACE
    | CHARSET
    | MEDIA
    | PAGE
    | CONTENT
    | MIXIN
    | IF
    | FOR
    | IMPORT
    | VARIABLES
    | DECLARATION
    | VAL_STRING
)
