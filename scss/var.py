from scss.base import Node, Empty, ParseNode
from scss.function import FUNCTION, unknown
from scss.value import Variable, NumberValue, Expression, BooleanValue


class VarDef(Empty):
    """ Variable definition.
    """
    def __init__(self, t, s):
        super(VarDef, self).__init__(t, s)
        name, self.value, default = self.data
        default = not isinstance(default, Empty)
        self.stylecheet.set_var(name, self.value, default)

    def copy(self, ctx=None):
        self.value.ctx = ctx
        return self


class Mixin(ParseNode, Empty):
    """ @mixin class.
    """

    def __init__(self, t, s=None):
        super(Mixin, self).__init__(t, s)
        self.stylecheet.mixctx[t[0]] = self

    def include(self, target, params):
        if isinstance(target, Mixin):
            return

        test = map(lambda x, y: (x, y), getattr(self, 'mixinparam', []), params)
        ctx = dict(( mp.name, v or mp.default ) for mp, v in test if mp)

        for e in self.data:
            if isinstance(e, ParseNode):
                node = e.copy(ctx)
                node.parse(target)


class Include(ParseNode):
    """ @include class.
    """

    def __init__(self, t, s):
        super(Include, self).__init__(t, s)
        self.mixin = s.mixctx.get(t[0])
        self.params = t[1:]

    def __str__(self):
        if not self.mixin is None:
            node = Node([])
            self.mixin.include(node, self.params)
            if hasattr(node, 'ruleset'):
                return ''.join(str(r) for r in getattr(node, 'ruleset'))

    def parse(self, target):
        if not self.mixin is None:
            self.mixin.include(target, self.params)


class Extend(ParseNode):
    """ @extend at rule.
    """
    def parse(self, target):
        name = str(self.data[0])
        rulesets = self.stylecheet.rset.get(name)
        if rulesets:
            for rul in rulesets:
                for sg in target.selectorgroup:
                    rul.selectorgroup.append(sg.increase(rul.selectorgroup[0]))


class Function(Variable):
    def __init__(self, t, s):
        super(Function, self).__init__(t, s)
        self.name, params = self.data[0], self.data[1:]
        self.params = list()
        for value in params:
            while isinstance(value, Variable):
                value = value.value
            self.params.append(value)

    @property
    def value(self):
        return self.__parse(self.ctx)

    def copy(self, ctx=None):
        return self.__parse(ctx)

    def __parse(self, ctx=dict()):
        func_name_a = "%s:%d" % (self.name, len(self.params))
        func_name_n = "%s:n" % self.name
        func = FUNCTION.get(func_name_a) or FUNCTION.get(func_name_n)
        return func(*self.params) if func else unknown(self.name, *self.params)

    def __str__(self):
        return str(self.__parse())


class IfNode(ParseNode):

    def __init__(self, t, s):
        super(IfNode, self).__init__(t, s)
        self.cond, self.body, self.els = self.data

    def __str__(self):
        return str(self.get_node())

    def get_node(self):
        data = self.cond.data
        if len(data) == 1:
            res = data[0]
        else:
            res = Expression.do_expression(data)
        return self.body if BooleanValue(res).value else self.els

    def parse(self, target):
        node = self.get_node()
        for n in node.data:
            n.parse(target)


class ForNode(ParseNode):
    def __init__(self, t, s):
        super(ForNode, self).__init__(t, s)
        self.var, self.first, self.second, self.body = self.data

    def copy(self, ctx=None):
        return self

    def __parse(self):
        name = self.var.data[1]
        for i in xrange(int(float( self.first )), int(float( self.second ))+1):
            yield self.body.copy({name: NumberValue(i)})

    def __str__(self):
        return ''.join(str(n) for n in self.__parse())

    def parse(self, target):
        for node in self.__parse():
            for n in node.data:
                if hasattr(n, 'parse'):
                    n.parse(target)
