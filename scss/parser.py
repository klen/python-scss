from collections import defaultdict

from scss.grammar import STYLESHEET, VARIABLE_ASSIGMENT, VAL_STRING, SELECTOR_GROUP, DECLARATION, DECLARESET, EXTEND, INCLUDE, MIXIN, MIXIN_PARAM, RULESET, COMMENT, VARIABLE, DEC_NAME, HEXCOLOR, LENGTH, PERCENTAGE, EMS, EXS
from scss.math import Length, Hexcolor


class Node(object):
    """ Base node for css object.
    """
    delim = ''

    def __init__(self, t, s=None):
        self.t = list(t)
        self.stylecheet = s
        self.parent = None
        self.context = None
        for e in self.t:
            if isinstance(e, Node):
                e.parse(self)

    def parse(self, target):
        name = self.__class__.__name__.lower()
        if not hasattr(target, name):
            setattr(target, name, list())
        getattr(target, name).append(self)
        self.parent = target

    def copy(self):
        return self.__class__(
            [ n.copy() if isinstance(n, Node) else n for n in self.t ],
            self.stylecheet
        )

    def getContext(self):
        if not self.context and self.parent:
            return self.parent.getContext()
        return self.context

    def __str__(self):
        return self.delim.join(str(e) for e in self.t)


class SelectorGroup(Node):
    """ Part of css rule.
    """
    delim = ' '

    def __add__(self, other):
        for s in other.t:
            if '&' in s:
                return SelectorGroup([s.replace('&', ' '.join(self.t)) for s in other.t])
        return SelectorGroup(self.t + other.t)



class Declaration(Node):
    """ Css declaration.
    """
    delim = ' '
    def __str__(self):
        return str(self.t[0]) + ': ' + ' '.join(str(e) for e in self.t[2:])


class Variable(Node):
    """ Get variable value.
    """
    @property
    def value(self):
        name = self.t[1]
        ctx = self.getContext()
        if ctx and ctx.get(name):
            value = ctx.get(name)
        else:
            value = self.stylecheet.context.get(name) or '0'
        return value

    def __str__(self):
        return str(self.value)


class VarString(Node):
    """ Parse mathematic operation.
    """
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
                    if isinstance(res, Variable):
                        res = res.value
                    if isinstance(arg, Variable):
                        arg = arg.value
                    res = res.math(arg, op)
            except StopIteration:
                op = False
        return res

    def __str__(self):
        return str(self.value)


class Ruleset(Node):

    def __init__(self, t, s):
        super(Ruleset, self).__init__(t, s)
        ancor = self.t[0].t[0]
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
            out += self.render_selectors()
            out += ' {\n\t'
            out += ';\n\t'.join(str(d) for d in self.declaration)
            out += '}\n\n'
        if hasattr(self, 'ruleset'):
            out += ''.join(str(r) for r in self.ruleset)
        return out

    def render_selectors(self):
        return ', '.join(str(s) for s in self.selectorgroup)


class DeclareSet(Node):

    def __init__(self, t, s):
        super(DeclareSet, self).__init__(t, s)
        if hasattr(self, "declaration"):
            for d in self.declaration:
                d.t[0].t.insert(0, self.t[0] + "-")

    def parse(self, target):
        for d in self.declaration:
            d.parse(target)


class Mixinparam(Node):
    @property
    def name(self):
        return self.t[0].t[1]

    @property
    def default(self):
        return self.t[1].value if len(self.t) > 1 else None


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

    def __str__(self):
        return ''

    def __len__(self):
        return False


class Include(Node):

    def __init__(self, t, s):
        super(Include, self).__init__(t, s)
        self.mixin = s.mix.get(t[0])
        self.params = t[1:]

    def parse(self, target):
        if not self.mixin is None:
            self.mixin.include(target, self.params)


class Extend(Node):
    """ @extend at rule.
    """
    def parse(self, target):
        name = self.t[0]
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
        COMMENT.setParseAction(self.comment)

        HEXCOLOR.setParseAction(self.getType(Hexcolor, style=False))
        LENGTH.setParseAction(self.getType(Length, style=False))
        EMS.setParseAction(self.getType(Length, style=False))
        EXS.setParseAction(self.getType(Length, style=False))
        PERCENTAGE.setParseAction(self.getType(Length, style=False))

        DEC_NAME.setParseAction(self.getType())

        VARIABLE.setParseAction(self.getType(Variable))
        VAL_STRING.setParseAction(self.getType(VarString))
        DECLARATION.setParseAction(self.getType(Declaration))
        SELECTOR_GROUP.setParseAction(self.getType(SelectorGroup))
        RULESET.setParseAction(self.getType(Ruleset))

        DECLARESET.setParseAction(self.getType(DeclareSet))
        MIXIN_PARAM.setParseAction(self.getType(Mixinparam))
        MIXIN.setParseAction(self.getType(Mixin))
        INCLUDE.setParseAction(self.getType(Include))
        EXTEND.setParseAction(self.getType(Extend))

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
        name, val_string = t
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
