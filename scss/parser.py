import cPickle
import logging
import os.path
from collections import defaultdict

from scss import SORTING
from scss.base import CopyNode, Empty, ParseNode, SimpleNode, SemiNode, SepValString, Node, warn
from scss.grammar import STYLESHEET, VAR_DEFINITION, EXPRESSION, SELECTOR_GROUP, DECLARATION, DECLARESET, EXTEND, INCLUDE, MIXIN, MIXIN_PARAM, RULESET, VARIABLE, DEC_NAME, HEXCOLOR, NUMBER_VALUE, SCSS_COMMENT, CSS_COMMENT, FUNCTION, IF, ELSE, IF_CONDITION, IF_BODY, SELECTOR, FOR, FOR_BODY, SEP_VAL_STRING, TERM, MEDIA, DEBUG, CHARSET, FONT_FACE, quotedString, IMPORT, VARIABLES, OPTION, WARN
from scss.value import NumberValue, ColorValue, Expression, Variable, QuotedStringValue, BooleanValue
from scss.var import Function, IfNode, ForNode, Mixin, Extend, Include, VarDef


class Comment(Node):
    def __str__(self):
        if self.root.get_opt('comments') and not self.root.get_opt('compress'):
            return super(Comment, self).__str__()
        return ''


class Import(SemiNode):
    pass
    # def __init__(self, t, s):
        # super(Import, self).__init__(t, s)
        # import ipdb; ipdb.set_trace() ### XXX Breakpoint ###


class Debug(Empty):
    def __init__(self, t, s):
        super(Debug, self).__init__(t, s)
        logging.debug(str(self))


class Option(Empty):
    def __init__(self, t, s):
        super(Option, self).__init__(t, s)
        opts = map(lambda (x, y): (x, BooleanValue(y).value),
                    zip(*[iter(self.data[1:])]*2)
                )
        for v in opts:
            self.root.set_opt(*v)


class SelectorGroup(ParseNode):
    """ Part of css rule.
    """
    def __init__(self, t, s=None):
        super(SelectorGroup, self).__init__(t, s)
        self.data = list(self.data)

    def increase(self, other):
        return SelectorGroup(list( self.data ) + other.data[1:])

    def parse(self, target):
        for x in str(self).split(','):
            target.selectorgroup.append(SelectorGroup( x.strip().split(' ') ))

    def __add__(self, other):
        test = str(other)
        if '&' in test:
            stest = str(self)
            return SelectorGroup(test.replace('&', stest).split())
        else:
            return SelectorGroup(self.data + other.data)


class DeclareSet(ParseNode):
    def __init__(self, t, s):
        self.declaration = []
        super(DeclareSet, self).__init__(t, s)

    def render(self, target):
        name = str(self.data[0])
        for dec in getattr(self, 'declareset', []):
            dec.render(self)
        for dc in self.declaration:
            dc.data[0].data[0] = "-".join((name, dc.data[0].data[0]))
            target.declaration.append(dc)


class Declaration(ParseNode):
    """ Css declaration.
    """
    def __str__(self):
        name, expr = ''.join(str(s) for s in self.data[0].data ), self.data[2:]
        if not SORTING.has_key(name.strip('*_')) and self.root.get_opt('warn'):
            warn("Unknown declaration: %s" % name)
        return ( ':' + self.root.delims[1] ).join([
            ''.join(str(s) for s in name),
            ' '.join(str(e) for e in expr)])


class FontFace(ParseNode):
    def __init__(self, t, s):
        self.declaration = []
        super(FontFace, self).__init__(t, s)

    def __str__(self):
        out = '\n@font-face {\n\t'
        self.declaration.sort(key=lambda x: str(x.data[0]))
        out += ';\n\t'.join(str(d) for d in self.declaration)
        out += '}\n'
        return out


class Ruleset(ParseNode):

    def __init__(self, t, s):
        self.declaration = []
        self.selectorgroup = []
        self.ruleset = []
        super(Ruleset, self).__init__(t, s)
        self.ancor = str(self.data[0].data[0])
        self.root.cache['rset'][self.ancor].add(self)

    def __repr__(self):
        return str(self)

    def parse(self, target):
        super(Ruleset, self).parse(target)
        if isinstance(target, Ruleset):
            self.parse_ruleset(target)

    def parse_ruleset(self, target):
        selgroup = list()
        for psg in target.selectorgroup:
            for sg in self.selectorgroup:
                selgroup.append(psg + sg)
        self.selectorgroup = selgroup

        for r in self.ruleset:
            r.parse_ruleset(target)

    def parse_declareset(self):
        for ds in getattr(self, 'declareset', []):
            ds.render(self)

    def __str__(self):
        self.parse_declareset()

        if self.root.get_opt('sort'):
            self.declaration.sort(key=lambda x: SORTING.get( str(x.data[0]), 999 ))

        nl, ws, ts = self.root.delims

        return ''.join((

            # Rule
            ''.join((

                # Selectors
                '\n' + ', '.join(str(s) for s in self.selectorgroup),

                # Declarations
                ws + '{' + nl + ts,
                (';' + nl + ts).join(
                    str(d) for d in self.declaration),
                '}' + nl

            )) if self.declaration else '',

            # Children rules
            ''.join(str(r) for r in self.ruleset)

        ))


class Mixinparam(ParseNode):
    @property
    def name(self):
        return self.data[0].data[0][1:]

    @property
    def default(self):
        if len(self.data) > 1:
            return self.data[1]
        return None


class Stylecheet(object):

    defvalue = NumberValue(0)
    defdelims = '\n', ' ', '\t'

    def __init__(self, cache = None, options=None):
        self.cache = cache or dict(

            # Variables context
            ctx = dict(),

            # Mixin context
            mix = dict(),

            # Options context
            opts = dict(
                comments = True,
                warn = True,
                sort = True,
            ),

            # Rules context
            rset = defaultdict(set),

            # CSS delimeters
            delims = self.defdelims,

            # Output
            out = ''
        )

        if options:
            for option in options.items():
                self.set_opt(*option)

        # Comments
        CSS_COMMENT.setParseAction(self.getType(Comment))
        SCSS_COMMENT.setParseAction(lambda s, l, t: '')

        # At rules
        WARN.setParseAction(warn)
        MEDIA.setParseAction(self.getType(SimpleNode))
        IMPORT.setParseAction(self.getType(Import))
        CHARSET.setParseAction(self.getType(SemiNode))
        FONT_FACE.setParseAction(self.getType(FontFace))
        OPTION.setParseAction(self.getType(Option))
        VARIABLES.setParseAction(Empty)

        # Values
        HEXCOLOR.setParseAction(ColorValue)
        NUMBER_VALUE.setParseAction(NumberValue)
        FUNCTION.setParseAction(self.getType(Function))
        quotedString.setParseAction(QuotedStringValue)
        VAR_DEFINITION.setParseAction(self.getType(VarDef))
        VARIABLE.setParseAction(self.getType(Variable))
        SEP_VAL_STRING.setParseAction(self.getType(SepValString))
        EXPRESSION.setParseAction(self.getType(Expression))

        # Declarations
        DEC_NAME.setParseAction(self.getType())
        TERM.setParseAction(self.getType())
        DECLARATION.setParseAction(self.getType(Declaration))
        DECLARESET.setParseAction(self.getType(DeclareSet))

        # Rules
        RULESET.setParseAction(self.getType(Ruleset))
        SELECTOR_GROUP.setParseAction(self.getType(SelectorGroup))
        SELECTOR.setParseAction(self.getType())

        # SCSS directives
        MIXIN_PARAM.setParseAction(self.getType(Mixinparam))
        MIXIN.setParseAction(self.getType(Mixin))
        INCLUDE.setParseAction(self.getType(Include))
        EXTEND.setParseAction(self.getType(Extend))
        IF.setParseAction(self.getType(IfNode))
        FOR.setParseAction(self.getType(ForNode))
        FOR_BODY.setParseAction(self.getType(ParseNode))
        IF_CONDITION.setParseAction(self.getType(ParseNode))
        IF_BODY.setParseAction(self.getType(ParseNode))
        ELSE.setParseAction(self.getType(ParseNode))

        DEBUG.setParseAction(self.getType(Debug))

    @property
    def delims(self):
        return self.cache['delims']

    def get_var(self, name):
        """ Get variable from global stylesheet context.
        """
        rec = self.cache['ctx'].get(name)
        if rec:
            return rec[0]

        # warn('Unwnown variable: %s' % name, self)
        return self.defvalue

    def set_opt(self, name, value):
        """ Set option.
            @option compress
            @option sort
            @option comments
        """
        self.cache['opts'][name] = value

        if name == 'compress':
            self.cache['delims'] = self.defdelims if not value else ('', '', '')

    def get_opt(self, name):
        """ Get option.
        """
        return self.cache['opts'].get(name)

    def set_var(self, name, value, default=False):
        """ Set variable to global stylesheet context.
        """
        if not(default and self.cache['ctx'].get(name)):
            if isinstance(value, Variable):
                value = value.value
            self.cache['ctx'][name] = value, default

    def dump(self):
        return cPickle.dumps(self.cache)

    def loads(self, src):
        """ Parse string and return self cache.
        """
        self.cache['out'] = STYLESHEET.transformString(src.strip()).strip()
        # self.cache['out'] = STYLESHEET.parseString(src.strip())
        return self.cache

    def update(self, cache):
        """ Update self cache from other.
        """
        self.cache['out'] += cache.get('out')
        self.cache['delims'] = cache.get('delims')
        self.cache['opts'].update(cache.get('opts'))
        self.cache['mix'].update(cache.get('mix'))
        self.cache['rset'].update(cache.get('rset'))
        for name, rec in cache['ctx'].items():
            self.set_var(name, *rec)

    def load(self, f, precache=None):

        precache = precache or self.get_opt('cache') or False
        cache_path = '.'

        if isinstance(f, str):
            cache_path = os.path.dirname(f)
            f = open(f)

        name = '.'.join(( os.path.splitext(f.name)[0], 'ccss' ))
        cache_path = os.path.join(cache_path, name)

        if precache and os.path.exists( cache_path ):
            ptime = os.path.getmtime(cache_path)
            ttime = os.path.getmtime(f.name)
            if ptime > ttime:
                dump = open(cache_path, 'rb').read()
                self.update(cPickle.loads(dump))
            return self.cache

        src = f.read()
        self.loads(src)
        if precache:
            f = open(cache_path, 'wb')
            f.write(self.dump())
        return self.cache

    def parse(self, src):
        self.loads(src)
        return self.cache['out']

    def getType(self, node=CopyNode, style=True):
        def wrap(s, l, t):
            if style:
                return node(t, self)
            return node(t)
        return wrap

    def __str__(self):
        return self.cache['out']


def parse( src, cache=None ):
    """ Parse from string.
    """
    parser = Stylecheet(cache)
    return parser.parse(src)


def load(path, cache=None, precache=False):
    """ Parse from file.
    """
    parser = Stylecheet(cache)
    cache = parser.load(path, precache=precache)
    return str(parser)
