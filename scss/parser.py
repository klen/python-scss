from collections import defaultdict
import ipdb as pdb

from scss.base import Node
from scss.function import Function, IfNode, ForNode
from scss.grammar import STYLESHEET, VARIABLE_ASSIGMENT, VAL_STRING, SELECTOR_GROUP, DECLARATION, DECLARESET, EXTEND, INCLUDE, MIXIN, MIXIN_PARAM, RULESET, VARIABLE, DEC_NAME, HEXCOLOR, LENGTH, PERCENTAGE, EMS, EXS, SCSS_COMMENT, CSS_COMMENT, FUNCTION, IF, ELSE, IF_CONDITION, IF_BODY, SELECTOR, FOR, FOR_BODY
from scss.value import Length, Color, Percentage


class Selector(Node):
    delim = ''

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

    def __str__(self):
        return str(self.value)


class VarString(Node):
    """ Parse mathematic operation.
    """
    @staticmethod
    def math(res, arg, op):
        if isinstance(res, str):
            if not res.isdigit():
                return res
            else:
                # Create fake length
                res = Length((res, 'px'))
        return res.math(arg, op)

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
                    if isinstance(res, (Variable, VarString)):
                        res = res.value
                    if isinstance(arg, (Variable, VarString)):
                        arg = arg.value
                    res = self.math(res, arg, op)
            except StopIteration:
                op = False
        return res

    def __str__(self):
        return str(self.value)


class Ruleset(Node):

    def __init__(self, t, s):
        super(Ruleset, self).__init__(t, s)
        ancor = str(self.t[0].t[0])
        self.stylecheet.ruleset[ancor].add(self)

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

    def __str__(self):
        out = ''
        if hasattr(self, 'declaration'):
            out += ', '.join(str(s) for s in self.selectorgroup)
            out += ' {\n\t'
            self.declaration.sort(key=lambda x: str(x.t[0]))
            out += ';\n\t'.join(str(d) for d in self.declaration)
            out += '}\n\n'
        if hasattr(self, 'ruleset'):
            out += ''.join(str(r) for r in self.ruleset)
        return out


class DeclareSet(Node):

    def parse(self, target):
        for d in getattr(self, 'declaration', []):
            if not isinstance(target, Mixin):
                d.t[0].t.insert(0, self.t[0] + "-")
                d.parse(target)


class Mixinparam(Node):
    @property
    def name(self):
        return self.t[0].t[1]

    @property
    def default(self):
        if len(self.t) > 1:
            return self.t[1].value
        return None


class Mixin(Node):

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

    def __len__(self):
        return False


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

    def __init__(self, context = None, mixin = None, ignore_comment=True):
        self.context = context or dict()
        self.ignore_comment = ignore_comment
        self.mix = mixin or dict()
        self.ruleset = defaultdict(set)
        self.t = None

        VARIABLE_ASSIGMENT.setParseAction(self.var_assigment)
        CSS_COMMENT.setParseAction(self.comment)
        SCSS_COMMENT.setParseAction(lambda s, l, t: False)

        HEXCOLOR.setParseAction(self.getType(Color, style=False))
        LENGTH.setParseAction(self.getType(Length, style=False))
        EMS.setParseAction(self.getType(Length, style=False))
        EXS.setParseAction(self.getType(Length, style=False))
        PERCENTAGE.setParseAction(self.getType(Percentage, style=False))

        DEC_NAME.setParseAction(self.getType())

        VARIABLE.setParseAction(self.getType(Variable))
        VAL_STRING.setParseAction(self.getType(VarString))
        DECLARATION.setParseAction(self.getType(Declaration))
        SELECTOR_GROUP.setParseAction(self.getType(SelectorGroup))
        SELECTOR.setParseAction(self.getType(Selector))
        RULESET.setParseAction(self.getType(Ruleset))

        DECLARESET.setParseAction(self.getType(DeclareSet))
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

    def parse(self, src):
        self.t = STYLESHEET.parseString(src)

    def render(self):
        out = delim = ''
        for e in self.t:
            if not e:
                continue
            if isinstance(e, str):
                if e in ";{}":
                    out += e + '\n'
                    delim = ''
                else:
                    out += delim + e
                    delim = ' '
            else:
                out += str(e)

        return out.strip()

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
        return False

    def comment(self, s, l, t):
        if self.ignore_comment:
            return False
        return t[0]

def parse( src, context=None ):
    parser = Stylecheet(context)
    parser.parse(src)
    return parser.render()
