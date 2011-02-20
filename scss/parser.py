import cPickle
import logging
import os.path
from collections import defaultdict

from scss import SORTING
from scss.base import CopyNode, Empty, ParseNode, SimpleNode, SemiNode, SepValString, Node
from scss.grammar import STYLESHEET, VAR_DEFINITION, EXPRESSION, SELECTOR_GROUP, DECLARATION, DECLARESET, EXTEND, INCLUDE, MIXIN, MIXIN_PARAM, RULESET, VARIABLE, DEC_NAME, HEXCOLOR, NUMBER_VALUE, SCSS_COMMENT, CSS_COMMENT, FUNCTION, IF, ELSE, IF_CONDITION, IF_BODY, SELECTOR, FOR, FOR_BODY, SEP_VAL_STRING, TERM, MEDIA, DEBUG, EMPTY, CHARSET, FONT_FACE, quotedString, IMPORT, VARIABLES, OPTION
from scss.value import NumberValue, ColorValue, Expression, Variable, QuotedStringValue, BooleanValue
from scss.var import Function, IfNode, ForNode, Mixin, Extend, Include, VarDef


class Comment(Node):
    def __str__(self):
        if self.root.ignore_comment:
            return ''
        return super(Comment, self).__str__()


class Debug(Empty):
    def __init__(self, t, s):
        super(Debug, self).__init__(t, s)
        logging.debug(str(self))


class Option(Empty):
    def __init__(self, t, s):
        super(Option, self).__init__(t, s)
        opts = dict(
                map(lambda (x, y): (x, BooleanValue(y).value),
                    zip(*[iter(self.data[1:])]*2)
                ))
        self.root.cache['opts'].update(opts)
        if self.root.cache['opts']['compress']:
            self.root.ws = self.root.nl = self.root.ts = ''
        else:
            self.root.ws, self.root.nl, self.root.ts = ' ', '\n', '\t'


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
        name, expr = self.data[0].data, self.data[2:]
        return ( ':' + self.root.ws ).join([
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
        self.declaration.sort(key=lambda x: SORTING.get( str(x.data[0]), 999 ))

        return ''.join((

            # Rule
            ''.join((

                # Selectors
                self.root.nl + ', '.join(str(s) for s in self.selectorgroup),

                # Declarations
                ' {' + self.root.nl + self.root.ts,
                (';' + self.root.nl + self.root.ts).join(
                    str(d) for d in self.declaration),
                '}' + '\n'

            )) if self.declaration else '',

            # Children rules
            ''.join(str(r) for r in self.ruleset)

        ))


class Mixinparam(ParseNode):
    @property
    def name(self):
        return self.data[0].data[1]

    @property
    def default(self):
        if len(self.data) > 1:
            return self.data[1]
        return None


class Stylecheet(object):

    defvalue = NumberValue(0)

    def __init__(self, cache = None, ignore_comment=False):
        self.cache = cache or dict(
            ctx = dict(),
            mix = dict(),
            opts = dict(
                compress = False,
                short_colors = True,
                sort = True,
            ),
            rset = defaultdict(set),
            out = ''
        )
        self.ignore_comment = ignore_comment
        self.nl, self.ws, self.ts = '\n', ' ', '\t'

        # Comments
        CSS_COMMENT.setParseAction(self.getType(Comment))
        SCSS_COMMENT.setParseAction(lambda s, l, t: '')

        # At rules
        MEDIA.setParseAction(self.getType(SimpleNode))
        IMPORT.setParseAction(self.getType(SemiNode))
        CHARSET.setParseAction(self.getType(SemiNode))
        FONT_FACE.setParseAction(self.getType(FontFace))
        OPTION.setParseAction(self.getType(Option))
        VARIABLES.setParseAction(Empty)

        # Values
        EMPTY.setParseAction(self.getType(Empty))
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

    def get_var(self, name):
        """ Get variable from global stylesheet context.
        """
        rec = self.cache['ctx'].get(name)
        return rec[0] if rec else self.defvalue

    def set_var(self, name, value, default=False):
        """ Set variable to global stylesheet context.
        """
        if not(default and self.cache['ctx'].get(name)):
            self.cache['ctx'][name] = value, default

    def __str__(self):
        return self.cache['out']

    def dump(self):
        return cPickle.dumps(self.cache)

    def loads(self, src):
        """ Parse string and return self cache.
        """
        self.cache['out'] = STYLESHEET.transformString(src.strip()).strip()
        return self.cache

    def update(self, cache):
        """ Update self cache from other.
        """
        self.cache['out'] += cache.get('out')
        self.cache['opts'].update(cache.get('opts'))
        self.cache['mix'].update(cache.get('mix'))
        self.cache['rset'].update(cache.get('rset'))
        for name, rec in cache['ctx'].items():
            self.set_var(name, *rec)

    def load(self, f, precache=False):
        name = os.path.splitext(f.name)[0]
        cache_path = '.'.join((name, 'ccss'))
        if os.path.exists(cache_path):
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
