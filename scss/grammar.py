from pyparsing import Word, Suppress, Literal, alphanums, SkipTo, oneOf, ZeroOrMore, Optional, OneOrMore, Forward, cStyleComment, Combine, dblSlashComment, quotedString, Regex, lineEnd, Group


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
FILE_PATH = Regex(r"[-\w\d_\.]*\/{1,2}[-\w\d_\.\/]*")
HTTP_PATH = Regex(r"((https?|ftp|file):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)")
PATH = FILE_PATH | HTTP_PATH

# Operators
MATH_OPERATOR = oneOf("+ - / * and or")
COMBINATOR = Word("+>", max=1)
IF_OPERATOR = oneOf("== != <= >= < > =")

# Values
EXPRESSION = Forward()
PARAMS = LPAREN + EXPRESSION + ZeroOrMore(COMMA + EXPRESSION) + RPAREN
FUNCTION = IDENT + PARAMS
INTERPOLATION_VAR = Suppress("#") + LACC + EXPRESSION + RACC
SIMPLE_VALUE = FUNCTION | NUMBER_VALUE | PATH | IDENT | HEXCOLOR | quotedString
VALUE = VARIABLE | SIMPLE_VALUE
DIV_STRING = SIMPLE_VALUE + OneOrMore(Literal("/") + SIMPLE_VALUE)
EXPRESSION << ((VALUE | PARAMS) + ZeroOrMore(MATH_OPERATOR + ( VALUE | PARAMS )))

# Declaration
TERM = ( DIV_STRING | EXPRESSION | INTERPOLATION_VAR ) + Optional(",")
DEC_NAME = Optional("*") + OneOrMore(IDENT | INTERPOLATION_VAR)
DECLARATION = DEC_NAME + ":" + OneOrMore(TERM) + Optional("!important") + OPT_SEMICOLON

# SCSS declareset
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
INCLUDE = "@include" + IDENT + Optional( PARAMS ) + OPT_SEMICOLON

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
MIXIN = "@mixin" + IDENT + Optional(MIXIN_PARAMS) + LACC + ZeroOrMore(CONTENT | FOR) + RACC
MIXIN = "@mixin" + IDENT + Optional(MIXIN_PARAMS) + LACC + ZeroOrMore(CONTENT | FOR) + RACC

# SCSS function
FUNCTION_RETURN = "@return" + VARIABLE + OPT_SEMICOLON
FUNCTION_BODY = LACC + ZeroOrMore(VAR_DEFINITION) + FUNCTION_RETURN + RACC
FUNCTION_DEFINITION = "@function" + IDENT + Group( MIXIN_PARAMS ) + FUNCTION_BODY

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
    | FUNCTION_DEFINITION
    | MIXIN
    | FOR
    | IMPORT
    | VARIABLES
    | EXPRESSION
)
