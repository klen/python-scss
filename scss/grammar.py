""" SCSS Grammars. """

from pyparsing import (
    Word, Suppress, Literal, alphanums, SkipTo, ZeroOrMore, Optional, OneOrMore,
    Forward, cStyleComment, Combine, dblSlashComment, quotedString, Regex,
    lineEnd, Group)


__all__ = (
    "CHARSET",
    "COLOR_VALUE",
    "CSS_COMMENT",
    "DECLARATION",
    "DECLARATION_NAME",
    "ELSE",
    "EXPRESSION",
    "EXTEND",
    "FONT_FACE",
    "FOR",
    "FOR_BODY",
    "FUNCTION",
    "FUNCTION_DEFINITION",
    "FUNCTION_RETURN",
    "IDENT",
    "IF",
    "IF_BODY",
    "IMPORT",
    "INCLUDE",
    "MEDIA",
    "MIXIN",
    "MIXIN_PARAM",
    "NUMBER_VALUE",
    "OPTION",
    "PATH",
    "POINT",
    "RULESET",
    "SCSS_COMMENT",
    "SELECTOR",
    "SELECTOR_GROUP",
    "SELECTOR_TREE",
    "SEP_VAL_STRING",
    "STYLESHEET",
    "VARIABLE",
    "VARIABLES",
    "VAR_DEFINITION",
    "WARN",
    "quotedString",
)


# Base css word and literals
COMMA, COLON, SEMICOLON = [Suppress(c) for c in ",:;"]
OPT_SEMICOLON = Optional(SEMICOLON)
LACC, RACC, LPAREN, RPAREN = [Suppress(c) for c in "{}()"]
LLACC, LRACC, LBRACK, RBRACK = [Literal(c) for c in "{}[]"]

# Comment
CSS_COMMENT = cStyleComment + Optional(lineEnd)
SCSS_COMMENT = dblSlashComment

IDENT = Regex(r"-?[a-zA-Z_][-a-zA-Z0-9_]*")
COLOR_VALUE = Regex(r"#[a-zA-Z0-9]{3,6}")
VARIABLE = Regex(r"-?\$[-a-zA-Z_][-a-zA-Z0-9_]*")
NUMBER_VALUE = Regex(r"-?\d+(?:\.\d*)?|\.\d+") + \
    Optional(Regex(r"(em|ex|px|cm|mm|in|pt|pc|deg|s|%)(?![-\w])"))
PATH = Regex(r"[-\w\d_\.]*\/{1,2}[-\w\d_\.\/\?\=\&]*") | Regex(
    r"((https?|ftp|file):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)")
POINT_PART = (NUMBER_VALUE | Regex(r"(top|bottom|left|right)"))
POINT = POINT_PART + POINT_PART

# Values
EXPRESSION = Forward()
INTERPOLATION_VAR = Suppress("#") + LACC + EXPRESSION + RACC
SIMPLE_VALUE = NUMBER_VALUE | PATH | IDENT | COLOR_VALUE | quotedString
DIV_STRING = SIMPLE_VALUE + OneOrMore(Literal("/") + SIMPLE_VALUE)

PARAMS = LPAREN + (POINT | EXPRESSION) + \
    ZeroOrMore(COMMA + (POINT | EXPRESSION)) + RPAREN
FUNCTION = Regex(r"-?[a-zA-Z_][-a-zA-Z0-9_]*") + PARAMS
VALUE = FUNCTION | VARIABLE | SIMPLE_VALUE
PARENS = LPAREN + EXPRESSION + RPAREN
MATH_OPERATOR = Regex(r"(\+|-|/|\*|and|or|==|!=|<=|<|>|>=)\s+")
_ = EXPRESSION << (
    (VALUE | PARENS) + ZeroOrMore(MATH_OPERATOR + (VALUE | PARENS)))

# Declaration
TERM = (DIV_STRING | EXPRESSION | INTERPOLATION_VAR) + Optional(",")
DECLARATION_NAME = Optional("*") + OneOrMore(IDENT | INTERPOLATION_VAR)
DECLARATION = Forward()
_ = DECLARATION << (
    DECLARATION_NAME +
    ":" +
    ZeroOrMore(TERM) +
    Optional("!important") +
    Optional(
        LACC +
        OneOrMore(
            DECLARATION | CSS_COMMENT | SCSS_COMMENT) +
        RACC) +
    OPT_SEMICOLON)

# Selectors
ELEMENT_NAME = Combine(OneOrMore(IDENT | '&')) | Literal("*")
ATTRIB = LBRACK + SkipTo("]") + RBRACK
CLASS_NAME = Word('.', alphanums + "-_")
HASH = Regex(r"#[-a-zA-Z_][-a-zA-Z0-9_]+")
FILTER = HASH | CLASS_NAME | ATTRIB

# PSEUDO = Regex(r':{1,2}[A-Za-z0-9-_]+')
PSEUDO = Regex(r':{1,2}[^\s;{}]+')

SELECTOR = OneOrMore(ELEMENT_NAME | FILTER | INTERPOLATION_VAR | PSEUDO)
SELECTOR.leaveWhitespace()
SELECTOR_GROUP = SELECTOR + ZeroOrMore(Optional(Word("+>", max=1)) + SELECTOR)
SELECTOR_GROUP.skipWhitespace = True
SELECTOR_TREE = SELECTOR_GROUP + ZeroOrMore(COMMA + SELECTOR_GROUP)

# @debug
DEBUG = "@debug" + EXPRESSION + OPT_SEMICOLON

# @warn
WARN = "@warn" + quotedString + OPT_SEMICOLON

# @include
INCLUDE = "@include" + IDENT + Optional(PARAMS) + OPT_SEMICOLON

# @extend
EXTEND = "@extend" + \
    OneOrMore(ELEMENT_NAME | FILTER | INTERPOLATION_VAR | PSEUDO) + OPT_SEMICOLON

# SCSS variable assigment
SEP_VAL_STRING = EXPRESSION + OneOrMore(COMMA + EXPRESSION)
VAR_DEFINITION = Regex(r"\$[a-zA-Z_][-a-zA-Z0-9_]*") + COLON + \
    (SEP_VAL_STRING | EXPRESSION) + Optional("!default") + OPT_SEMICOLON

RULESET = Forward()
IF = Forward()
CONTENT = CSS_COMMENT | SCSS_COMMENT | WARN | DEBUG | IF | INCLUDE \
    | VAR_DEFINITION | RULESET | DECLARATION

# SCSS control directives
IF_BODY = LACC + ZeroOrMore(CONTENT) + RACC
ELSE = Suppress("@else") + LACC + ZeroOrMore(CONTENT) + RACC
_ = IF << (
    (Suppress("@if") | Suppress("@else if")) +
    EXPRESSION +
    IF_BODY +
    Optional(ELSE))

FOR_BODY = ZeroOrMore(CONTENT)
FOR = "@for" + VARIABLE + \
    Suppress("from") + VALUE + (Suppress("through") | Suppress("to")) \
    + VALUE + LACC + FOR_BODY + RACC

_ = RULESET << (
    SELECTOR_TREE +
    LACC + ZeroOrMore(CONTENT | FOR | EXTEND) + RACC)

# SCSS mixin
MIXIN_PARAM = VARIABLE + Optional(COLON + EXPRESSION)
MIXIN_PARAMS = LPAREN + ZeroOrMore(COMMA | MIXIN_PARAM) + RPAREN
MIXIN = "@mixin" + IDENT + \
    Group(Optional(MIXIN_PARAMS)) + LACC + ZeroOrMore(CONTENT | FOR) + RACC

# SCSS function
FUNCTION_RETURN = "@return" + VARIABLE + OPT_SEMICOLON
FUNCTION_BODY = LACC + ZeroOrMore(VAR_DEFINITION) + FUNCTION_RETURN + RACC
FUNCTION_DEFINITION = "@function" + IDENT + Group(MIXIN_PARAMS) + FUNCTION_BODY

# Root elements
OPTION = "@option" + \
    OneOrMore(IDENT + COLON + IDENT + Optional(COMMA)) + OPT_SEMICOLON
IMPORT = "@import" + FUNCTION + OPT_SEMICOLON
MEDIA = "@media" + IDENT + \
    ZeroOrMore("," + IDENT) + LLACC + ZeroOrMore(CONTENT | MIXIN | FOR) + LRACC
FONT_FACE = "@font-face" + LLACC + ZeroOrMore(DECLARATION) + LRACC
VARIABLES = (Literal("@variables") | Literal('@vars')) + \
    LLACC + ZeroOrMore(VAR_DEFINITION) + RACC
PSEUDO_PAGE = ":" + IDENT
PAGE = "@page" + Optional(IDENT) + Optional(PSEUDO_PAGE) + \
    LLACC + ZeroOrMore(DECLARATION) + LRACC
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
