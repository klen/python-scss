from __future__ import print_function

import os.path
import sys

from collections import defaultdict
from pyparsing import ParseBaseException

from . import SORTING
from .base import Node, Empty, ParseNode, ContentNode, IncludeNode
from .compat import pickle, bytes_, unicode_, file_
from .control import (
    Variable, Expression, Function, Mixin, Include, MixinParam, Extend,
    Variables, Option, FunctionDefinition, FunctionReturn, If, For, SepValString)
from .function import warn, _nest
from .grammar import *
from .value import NumberValue, StringValue, ColorValue, QuotedStringValue, PointValue


class Comment(Node):

    """ Comment node.
    """
    delim = ''

    def __str__(self):
        """ Clean comments if option `comments` disabled
            or enabled option `compress`
        """
        if self.root.get_opt('comments') and not self.root.get_opt('compress'):
            return super(Comment, self).__str__()
        return ''


class Warn(Empty):

    """ Warning node @warn.
    """

    def parse(self, target):
        """ Write message to stderr.
        """
        if self.root.get_opt('warn'):
            warn(self.data[1])


class Import(Node):

    """ Import node @import.
    """

    def __str__(self):
        """ Write @import to outstring.
        """
        return "%s;\n" % super(Import, self).__str__()


class Ruleset(ContentNode):

    """ Rule node.
    """

    def parse(self, target):
        """ Parse nested rulesets
            and save it in cache.
        """
        if isinstance(target, ContentNode):
            if target.name:
                self.parent = target
                self.name.parse(self)
                self.name += target.name
            target.ruleset.append(self)
        self.root.cache['rset'][str(self.name).split()[0]].add(self)
        super(Ruleset, self).parse(target)


class Declaration(ParseNode):

    """ Declaration node.
    """

    def __init__(self, s, n, t):
        """ Add self.name and self.expr to object.
        """
        super(Declaration, self).__init__(s, n, t)
        self.name = self.expr = ''

    def parse(self, target):
        """ Parse nested declaration.
        """
        if not isinstance(target, Node):
            parent = ContentNode(None, None, [])
            parent.parse(target)
            target = parent

        super(Declaration, self).parse(target)
        self.name = str(self.data[0])
        while isinstance(target, Declaration):
            self.name = '-'.join((str(target.data[0]), self.name))
            target = target.parent

        self.expr = ' '.join(str
                             (n)
                             for n in self.data
                             [2:] if not isinstance(n, Declaration))
        if self.expr:
            target.declareset.append(self)

    def __str__(self):
        """ Warning on unknown declaration
            and write current in outstring.
        """
        name = self.name.strip('*_#')
        if name.startswith('-moz-'):
            name = name[5:]
        elif name.startswith('-webkit-'):
            name = name[8:]
        elif name.startswith('-o-'):
            name = name[3:]
        elif name.startswith('-ms-'):
            name = name[4:]

        if name not in SORTING and self.root.get_opt('warn'):
            warn("Unknown declaration: %s" % self.name)

        return (":%s" % self.root.cache['delims'][1]).join(
            (self.name, self.expr))


class DeclarationName(ParseNode):

    """ Name of declaration node.
        For spliting it in one string.
    """
    delim = ''


class SelectorTree(ParseNode):

    """ Tree of selectors in ruleset.
    """
    delim = ', '

    def extend(self, target):
        """ @extend selectors tree.
        """
        self_test = ', '.join(map(str, self.data))
        target_test = ', '.join(map(str, target.data))
        self.data = (
            self_test + ', ' + self_test.replace(str(self.data[0].data[0]),
                                                 target_test)).split(', ')

    def __add__(self, target):
        """ Add selectors from parent nodes.
        """
        if isinstance(target, SelectorTree):
            self_test = ', '.join(map(str, self.data))
            target_test = ', '.join(map(str, target.data))
            self.data = _nest(target_test, self_test).split(', ')
        return self


class Selector(ParseNode):

    """ Simple selector node.
    """
    delim = ''

    def __str__(self):
        """ Write to output.
        """
        return ''.join(StringValue(n).value for n in self.data)


class VarDefinition(ParseNode, Empty):

    """ Variable definition.
    """

    def __init__(self, s, n, t):
        """ Save self.name, self.default, self.expression
        """
        super(VarDefinition, self).__init__(s, n, t)
        self.name = t[0][1:]
        self.default = len(t) > 2
        self.expression = t[1]

    def parse(self, target):
        """ Update root and parent context.
        """
        super(VarDefinition, self).parse(target)
        if isinstance(self.parent, ParseNode):
            self.parent.ctx.update({self.name: self.expression.value})
        self.root.set_var(self)


class Stylesheet(object):

    """ Root stylesheet node.
    """

    def_delims = '\n', ' ', '\t'

    def __init__(self, cache=None, options=None):
        self.cache = cache or dict(

            # Variables context
            ctx=dict(),

            # Mixin context
            mix=dict(),

            # Rules context
            rset=defaultdict(set),

            # Options context
            opts=dict(
                comments=True,
                warn=True,
                sort=True,
                path=os.getcwd(),
            ),

            # CSS delimeters
            delims=self.def_delims,

        )

        if options:
            for option in options.items():
                self.set_opt(*option)

        self.setup()
        Node.root = self

    @staticmethod
    def setup():

        # Values
        NUMBER_VALUE.setParseAction(NumberValue)
        IDENT.setParseAction(StringValue)
        PATH.setParseAction(StringValue)
        POINT.setParseAction(PointValue)
        COLOR_VALUE.setParseAction(ColorValue)
        quotedString.setParseAction(QuotedStringValue)
        EXPRESSION.setParseAction(Expression)
        SEP_VAL_STRING.setParseAction(SepValString)

        # Vars
        VARIABLE.setParseAction(Variable)
        VAR_DEFINITION.setParseAction(VarDefinition)
        VARIABLES.setParseAction(Variables)
        FUNCTION.setParseAction(Function)
        FUNCTION_DEFINITION.setParseAction(FunctionDefinition)
        FUNCTION_RETURN.setParseAction(FunctionReturn)

        # Coments
        SCSS_COMMENT.setParseAction(lambda x: '')
        CSS_COMMENT.setParseAction(Comment)

        # At rules
        IMPORT.setParseAction(Import)
        CHARSET.setParseAction(Import)
        MEDIA.setParseAction(Node)

        # Rules
        RULESET.setParseAction(Ruleset)
        DECLARATION.setParseAction(Declaration)
        DECLARATION_NAME.setParseAction(DeclarationName)
        SELECTOR.setParseAction(Selector)
        SELECTOR_GROUP.setParseAction(ParseNode)
        SELECTOR_TREE.setParseAction(SelectorTree)
        FONT_FACE.setParseAction(ContentNode)

        # SCSS Directives
        MIXIN.setParseAction(Mixin)
        MIXIN_PARAM.setParseAction(MixinParam)
        INCLUDE.setParseAction(Include)
        EXTEND.setParseAction(Extend)
        OPTION.setParseAction(Option)
        IF.setParseAction(If)
        IF_BODY.setParseAction(IncludeNode)
        ELSE.setParseAction(IncludeNode)
        FOR.setParseAction(For)
        FOR_BODY.setParseAction(IncludeNode)
        WARN.setParseAction(Warn)

    @property
    def ctx(self):
        return self.cache['ctx']

    def set_var(self, vardef):
        """ Set variable to global stylesheet context.
        """
        if not(vardef.default and self.cache['ctx'].get(vardef.name)):
            self.cache['ctx'][vardef.name] = vardef.expression.value

    def set_opt(self, name, value):
        """ Set option.
        """
        self.cache['opts'][name] = value

        if name == 'compress':
            self.cache['delims'] = self.def_delims if not value else (
                '',
                '',
                '')

    def get_opt(self, name):
        """ Get option.
        """
        return self.cache['opts'].get(name)

    def update(self, cache):
        """ Update self cache from other.
        """
        self.cache['delims'] = cache.get('delims')
        self.cache['opts'].update(cache.get('opts'))
        self.cache['rset'].update(cache.get('rset'))
        self.cache['mix'].update(cache.get('mix'))
        map(self.set_var, cache['ctx'].values())

    @staticmethod
    def scan(src):
        """ Scan scss from string and return nodes.
        """
        assert isinstance(src, (unicode_, bytes_))
        try:
            nodes = STYLESHEET.parseString(src, parseAll=True)
            return nodes
        except ParseBaseException:
            err = sys.exc_info()[1]
            print(err.line, file=sys.stderr)
            print(" " * (err.column - 1) + "^", file=sys.stderr)
            print(err, file=sys.stderr)
            sys.exit(1)

    def parse(self, nodes):
        for n in nodes:
            if isinstance(n, Node):
                n.parse(self)

    def loads(self, src):
        """ Compile css from scss string.
        """
        assert isinstance(src, (unicode_, bytes_))
        nodes = self.scan(src.strip())
        self.parse(nodes)
        return ''.join(map(str, nodes))

    def load(self, f, precache=None):
        """ Compile scss from file.
            File is string path of file object.
        """
        precache = precache or self.get_opt('cache') or False
        nodes = None
        if isinstance(f, file_):
            path = os.path.abspath(f.name)

        else:
            path = os.path.abspath(f)
            f = open(f)

        cache_path = os.path.splitext(path)[0] + '.ccss'

        if precache and os.path.exists(cache_path):
            ptime = os.path.getmtime(cache_path)
            ttime = os.path.getmtime(path)
            if ptime > ttime:
                dump = open(cache_path, 'rb').read()
                nodes = pickle.loads(dump)

        if not nodes:
            src = f.read()
            nodes = self.scan(src.strip())

        if precache:
            f = open(cache_path, 'wb')
            pickle.dump(nodes, f, protocol=1)

        self.parse(nodes)
        return ''.join(map(str, nodes))


def parse(src, cache=None):
    """ Parse from string.
    """
    parser = Stylesheet(cache)
    return parser.loads(src)


def load(path, cache=None, precache=False):
    """ Parse from file.
    """
    parser = Stylesheet(cache)
    return parser.load(path, precache=precache)

# pylama:ignore=D,W0401
