from pyparsing import Word, Suppress, Literal, alphanums, SkipTo, oneOf, ZeroOrMore, Optional, OneOrMore, Forward, cStyleComment, Combine, dblSlashComment, quotedString, Regex, lineEnd


# Base css word and literals
COMMA, COLON, SEMICOLON = [Suppress(c) for c in ",:;"]
OPT_SEMICOLON = Optional(SEMICOLON)
LACC, RACC, LPAREN, RPAREN = [Suppress(c) for c in "{}()"]
LLACC, LRACC, LBRACK, RBRACK = [Literal(c) for c in "{}[]"]

# Comment
CSS_COMMENT = cStyleComment + Optional(lineEnd)
SCSS_COMMENT = dblSlashComment
COMMENT = CSS_COMMENT | SCSS_COMMENT

IDENT = Regex(r"-?[a-zA-Z_][-a-zA-Z0-9_]*")
NUMBER = Regex(r"-?\d+(?:\.\d*)?|\.\d+")
HASH = Regex(r"#[-a-zA-Z_][-a-zA-Z0-9_]+")
HEXCOLOR = Regex(r"#[a-zA-Z0-9]{3,6}")
VARIABLE = Regex(r"-?\$[-a-zA-Z_][-a-zA-Z0-9_]*")
NUMBER_VALUE = NUMBER + Optional(oneOf("em ex px cm mm in pt pc deg % "))
PATH = Word(alphanums + "_-/.", alphanums + "_-./?#&")

# Operators
MATH_OPERATOR = oneOf("+ - / * and or")
COMBINATOR = Word("+>", max=1)
IF_OPERATOR = oneOf("== != <= >= < > =")

# Values
EXPRESSION = Forward()
FUNCTION = IDENT + LPAREN + ZeroOrMore(COMMA | EXPRESSION) + RPAREN
INTERPOLATION_VAR = Suppress("#") + LACC + EXPRESSION + RACC
SIMPLE_VALUE = FUNCTION | IDENT | NUMBER_VALUE | PATH | HEXCOLOR | quotedString
VALUE = VARIABLE | SIMPLE_VALUE
DIV_STRING = SIMPLE_VALUE + OneOrMore(Literal("/") + SIMPLE_VALUE)
PARENS = LPAREN + EXPRESSION + RPAREN
EXPRESSION << ((VALUE | PARENS) + ZeroOrMore(MATH_OPERATOR + ( VALUE | PARENS )))

# Property values
TERM = ( DIV_STRING | EXPRESSION | INTERPOLATION_VAR ) + Optional(",")
EXPR = OneOrMore(TERM) + Optional("!important")
DEC_NAME = Optional("*") + OneOrMore(IDENT | INTERPOLATION_VAR)
DECLARATION = DEC_NAME + ":" + EXPR + OPT_SEMICOLON

# SCSS group of declarations
DECLARESET = Forward()
DECLARESET << DEC_NAME + COLON + LACC + OneOrMore(DECLARESET | DECLARATION | COMMENT) + RACC + OPT_SEMICOLON

# Selectors
ELEMENT_NAME = Combine(OneOrMore(IDENT | '&')) | Literal("*")
ATTRIB = LBRACK + SkipTo("]") + RBRACK
CLASS_NAME = Word('.', alphanums + "-_")
FILTER = HASH | CLASS_NAME | ATTRIB
PSEUDO = Regex(r':{1,2}[A-Za-z0-9-_]+')
SELECTOR = OneOrMore(ELEMENT_NAME | FILTER | INTERPOLATION_VAR | PSEUDO)
SELECTOR.leaveWhitespace()
SELECTOR_GROUP = SELECTOR + ZeroOrMore(Optional(COMBINATOR) + SELECTOR)
SELECTOR_GROUP.skipWhitespace = True
SELECTOR_TREE = SELECTOR_GROUP + ZeroOrMore(COMMA + SELECTOR_GROUP)

# @debug
DEBUG = "@debug" + EXPRESSION + OPT_SEMICOLON

# @warn
WARN = "@warn" + quotedString + OPT_SEMICOLON

# @include
INCLUDE = "@include" + IDENT + Optional(LPAREN + ZeroOrMore(COMMA | EXPRESSION) + RPAREN) + OPT_SEMICOLON

# @extend
EXTEND = "@extend" + OneOrMore(ELEMENT_NAME | FILTER | INTERPOLATION_VAR | PSEUDO) + OPT_SEMICOLON

# SCSS variable assigment
SEP_VAL_STRING = EXPRESSION + OneOrMore(COMMA + EXPRESSION)
VAR_DEFINITION = Suppress("$") + IDENT + COLON + (SEP_VAL_STRING | EXPRESSION ) + Optional("!default") + OPT_SEMICOLON

RULESET = Forward()
IF = Forward()
CONTENT = COMMENT | WARN | DEBUG | IF | INCLUDE | VAR_DEFINITION | RULESET | DECLARESET | DECLARATION

# SCSS control directives
IF_CONDITION = EXPRESSION + Optional(IF_OPERATOR + EXPRESSION)
IF_BODY = LACC + ZeroOrMore(CONTENT) + RACC
ELSE = Suppress("@else") + LACC + ZeroOrMore(CONTENT) + RACC
IF << (
        ( Suppress("@if") | Suppress("@else if") ) + IF_CONDITION + IF_BODY + Optional(ELSE))

FOR_BODY = ZeroOrMore(CONTENT)
FOR = "@for" + VARIABLE + Suppress("from") + VALUE + (Suppress("through") | Suppress("to")) + VALUE + LACC + FOR_BODY + RACC

RULESET << (
    SELECTOR_TREE +
    LACC + ZeroOrMore(CONTENT | FOR | EXTEND) + RACC )

# SCSS mixin
MIXIN_PARAM = VARIABLE + Optional(COLON + EXPRESSION)
MIXIN_PARAMS = LPAREN + ZeroOrMore(COMMA | MIXIN_PARAM) + RPAREN
MIXIN = ("@mixin" + IDENT + Optional(MIXIN_PARAMS) +
    LACC + ZeroOrMore(CONTENT | FOR) + RACC)

# Root elements
OPTION = "@option" + OneOrMore(IDENT + COLON + IDENT + Optional(COMMA)) + OPT_SEMICOLON
IMPORT = "@import" + FUNCTION + OPT_SEMICOLON
MEDIA = "@media" + IDENT + ZeroOrMore("," + IDENT) + LLACC + ZeroOrMore( CONTENT | MIXIN | FOR ) + LRACC
FONT_FACE = "@font-face" + LLACC + ZeroOrMore(DECLARATION) + LRACC
VARIABLES = ( Literal("@variables") | Literal('@vars') ) + LLACC + ZeroOrMore(VAR_DEFINITION) + RACC
PSEUDO_PAGE = ":" + IDENT
PAGE = "@page" + Optional(IDENT) + Optional(PSEUDO_PAGE) + LLACC + ZeroOrMore(DECLARATION) + LRACC
CHARSET = "@charset" + IDENT + OPT_SEMICOLON

# Css stylesheet
STYLESHEET = ZeroOrMore(
    FONT_FACE
    | CHARSET
    | OPTION
    | MEDIA
    | PAGE
    | CONTENT
    | MIXIN
    | FOR
    | IMPORT
    | VARIABLES
    | EXPRESSION
)
