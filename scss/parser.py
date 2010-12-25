import logging
from collections import defaultdict

from scss.base import Node
from scss.function import Function, IfNode, ForNode
from scss.grammar import STYLESHEET, VARIABLE_ASSIGMENT, VAL_STRING, SELECTOR_GROUP, DECLARATION, DECLARESET, EXTEND, INCLUDE, MIXIN, MIXIN_PARAM, RULESET, VARIABLE, DEC_NAME, HEXCOLOR, LENGTH, PERCENTAGE, EMS, EXS, SCSS_COMMENT, CSS_COMMENT, FUNCTION, IF, ELSE, IF_CONDITION, IF_BODY, SELECTOR, FOR, FOR_BODY, SIMPLE_STRING, DIV_STRING, MEDIA, DEBUG, EMPTY
from scss.value import Length, Color, Percentage, Value


class SimpleNode(Node):
    delim = ''

class AtRule(Node):
    delim = ' '

class Comment(Node):
    def __str__(self):
        if self.stylecheet.ignore_comment:
            return ''
        return "\n%s\n" % super(Comment, self).__str__()

class Empty(Node):
    def __str__(self):
        return ''

class Debug(Empty):
    def __init__(self, t, s):
        super(Debug, self).__init__(t, s)
        logging.debug(str(self))

class DeclareSet(Node):
    def render(self, target):
        self.declaration = self.declaration or []
        name = self.t[0]
        for dec in getattr(self, 'declareset', []):
            dec.render(self)
        for dc in self.declaration:
            dc.t[0].t[0] = "-".join((name, dc.t[0].t[0]))
            target.declaration.append(dc)

class SelectorGroup(Node):
    """ Part of css rule.
    """
    def __add__(self, other):
        test = str(other)
        if '&' in test:
            stest = str(self)
            node = SelectorGroup(test.replace('&', stest).split())
        else:
            node = SelectorGroup(self.t + other.t)
        ctx1, ctx2 = self.getContext(), other.getContext()
        if ctx1 or ctx2:
            node.context = ctx1.update(ctx2 or {}) if ctx1 else ctx2
        return node

class Declaration(Node):
    """ Css declaration.
    """
    def __str__(self):
        name, expr = self.t[0].t, self.t[2:]
        return ': '.join([
            ''.join(str(s) for s in name),
            ' '.join(str(e) for e in expr)])

class Variable(Node):
    """ Get variable value.
    """
    @property
    def value(self):
        name = self.t[1]
        ctx = self.getContext()
        if ctx and ctx.get(name):
            return ctx.get(name)
        return self.stylecheet.context.get(name) or '0'

    def math(self, arg, op):
        if isinstance(self.value, (int, str)):
            return Length((str(self.value), 'px')).math(arg, op)
        return self.value.math(arg, op)

    def __str__(self):
        return str(self.value)

    def __int__(self):
        try:
            return int(self.value)
        except ValueError:
            return 0

    def __float__(self):
        try:
            return float(self.value)
        except ValueError:
            return 0

class VarString(Variable):
    """ Parse mathematic operation.
    """
    @staticmethod
    def math(res, arg, op):
        if isinstance(res, (Node, Value)):
            return res.math(arg, op)
        return Length((str(res), 'px')).math(arg, op)

    @property
    def value(self):
        it = iter(self.t)
        res = next(it)
        op = True
        while op:
            try:
                op = next(it)
                if op in "+-/*":
                    arg = next(it)
                    res = self.math(res, arg, op)
            except StopIteration:
                op = False
        return res

class Ruleset(Node):

    def __init__(self, t, s):
        self.declaration = []
        super(Ruleset, self).__init__(t, s)
        ancor = str(self.t[0].t[0])
        self.stylecheet.ruleset[ancor].add(self)
        # self.tab = '\t'

    def parse(self, target):
        super(Ruleset, self).parse(target)
        if isinstance(target, Ruleset):
            self.parse_ruleset(target)
            for r in getattr(self, 'ruleset', []):
                r.parse_ruleset(target)

    def parse_ruleset(self, target):
        selgroup = list()
        for psg in target.selectorgroup:
            for sg in self.selectorgroup:
                selgroup.append(psg + sg)
        self.selectorgroup = selgroup

    def parse_declareset(self):
        for ds in getattr(self, 'declareset', []):
            ds.render(self)

    def __str__(self):
        out = ''
        self.parse_declareset()
        if len(self.declaration):
            out = '\n'
            out += ', '.join(str(s) for s in self.selectorgroup)
            out += ' {\n\t'
            self.declaration.sort(key=lambda x: str(x.t[0]))
            out += ';\n\t'.join(str(d) for d in self.declaration)
            out += '}\n'
        # for r in getattr(self, 'ruleset', []):
            # out += '\n'.join("%s%s" % (self.tab, l) for l in str(r).split('\n'))
        if hasattr(self, 'ruleset'):
            out += ''.join(str(r) for r in self.ruleset)
        return out

class Mixinparam(Node):
    @property
    def name(self):
        return self.t[0].t[1]

    @property
    def default(self):
        if len(self.t) > 1:
            return self.t[1].value
        return None

class Mixin(Empty):

    def __init__(self, t, s=None):
        super(Mixin, self).__init__(t, s)
        s.mix[self.t[0]] = self

    def include(self, target, params):
        test = map(lambda x, y: (x, y), getattr(self, 'mixinparam', []), params)
        ctx = dict(( mp.name, v or mp.default ) for mp, v in test if mp)

        for e in self.t:
            if isinstance(e, Node):
                node = e.copy()
                node.context = ctx
                node.parse(target)

class Include(Node):

    def __init__(self, t, s):
        super(Include, self).__init__(t, s)
        self.mixin = s.mix.get(t[0])
        self.params = t[1:]

    def __str__(self):
        out = ''
        if not self.mixin is None:
            node = Node([])
            self.parse(node)
            for r in getattr(node, 'ruleset', []):
                out += str(r)
        return out

    def parse(self, target):
        if not self.mixin is None:
            self.mixin.include(target, self.params)

class Extend(Node):
    """ @extend at rule.
    """
    def parse(self, target):
        name = str(self.t[0])
        rulesets = self.stylecheet.ruleset.get(name)
        if rulesets:
            for rul in rulesets:
                selgroup = SelectorGroup(
                    target.selectorgroup[0].t + rul.selectorgroup[0].t[1:])
                rul.selectorgroup.append(selgroup)

class Stylecheet(object):

    def __init__(self, context = None, mixin = None, ignore_comment=False):
        self.context = context or dict()
        self.ignore_comment = ignore_comment
        self.mix = mixin or dict()
        self.ruleset = defaultdict(set)
        self.t = None

        VARIABLE_ASSIGMENT.setParseAction(self.var_assigment)
        CSS_COMMENT.setParseAction(self.getType(Comment))
        SCSS_COMMENT.setParseAction(lambda s, l, t: '')

        MEDIA.setParseAction(self.getType(AtRule))
        EMPTY.setParseAction(self.getType(Empty))

        HEXCOLOR.setParseAction(self.getType(Color, style=False))
        LENGTH.setParseAction(self.getType(Length, style=False))
        EMS.setParseAction(self.getType(Length, style=False))
        EXS.setParseAction(self.getType(Length, style=False))
        PERCENTAGE.setParseAction(self.getType(Percentage, style=False))

        DEC_NAME.setParseAction(self.getType())
        SIMPLE_STRING.setParseAction(self.getType(SimpleNode))
        DIV_STRING.setParseAction(self.getType(SimpleNode))

        VARIABLE.setParseAction(self.getType(Variable))
        VAL_STRING.setParseAction(self.getType(VarString))
        DECLARATION.setParseAction(self.getType(Declaration))
        DECLARESET.setParseAction(self.getType(DeclareSet))
        SELECTOR_GROUP.setParseAction(self.getType(SelectorGroup))
        SELECTOR.setParseAction(self.getType(SimpleNode))
        RULESET.setParseAction(self.getType(Ruleset))

        MIXIN_PARAM.setParseAction(self.getType(Mixinparam))
        MIXIN.setParseAction(self.getType(Mixin))
        INCLUDE.setParseAction(self.getType(Include))
        EXTEND.setParseAction(self.getType(Extend))

        IF.setParseAction(self.getType(IfNode))
        FOR.setParseAction(self.getType(ForNode))
        FOR_BODY.setParseAction(self.getType())
        IF_CONDITION.setParseAction(self.getType())
        IF_BODY.setParseAction(self.getType())
        ELSE.setParseAction(self.getType())
        FUNCTION.setParseAction(self.getType(Function))
        DEBUG.setParseAction(self.getType(Debug))

    def parse(self, src):
        return STYLESHEET.transformString(src).strip()

    def getType(self, node=Node, style=True):
        def wrap(s, l, t):
            if style:
                return node(t, self)
            return node(t)
        return wrap

    def var_assigment(self, s, l, t):
        name, val_string, default = t[0], t[1], False if len(t) < 3 else True
        if not(default and self.context.get(name)):
            self.context[name] = val_string.value
        return ''

def parse( src, context=None ):
    parser = Stylecheet(context)
    return parser.parse(src)
