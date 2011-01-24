from scss.base import Node, Empty
from scss.value import Length


class VarDef(Empty):
    """ Variable definition.
    """
    def __init__(self, t, s):
        super(VarDef, self).__init__(t, s)
        name, self.value, default = t
        default = not isinstance(default, Empty)
        s.set_var(name, self.value, default)

    def parse(self, target):
        pass

    def copy(self, ctx=None):
        self.value.ctx = ctx
        return self


class Variable(Node):
    """ Get variable value.
    """
    def __init__(self, t, s):
        super(Variable, self).__init__(t, s)
        self.ctx = None

    def copy(self, ctx=None):
        self.ctx = ctx
        if isinstance(self.value, Node):
            return self.value.copy(ctx)
        return self.value

    @property
    def value(self):
        name = self.t[1]
        if self.ctx and self.ctx.get(name):
            return self.ctx.get(name)
        return self.stylecheet.get_var(name) or '0'

    def math(self, arg, op):
        if isinstance(self.value, (int, str)):
            return Length((str(self.value), 'px')).math(arg, op)
        return self.value.math(arg, op)

    def __str__(self):
        return str(self.value)

    def __int__(self):
        return int(float(self))

    def __float__(self):
        try:
            return float(self.value)
        except (ValueError, RuntimeError):
            return 0.0


class SepValString(Node):
    """ Separeted value.
    """
    delim = ', '
    def math(self, arg, op):
        return self


class VarString(Variable):
    """ Parse mathematic operation.
    """
    @property
    def value(self):

        for n in self.t:
            if isinstance(n, Variable):
                n.ctx = self.ctx

        it = iter(self.t)
        res = next(it)
        op = True
        while op:
            try:
                op = next(it)
                if op in "+-/*":
                    arg = next(it)
                    if isinstance(res, str):
                        res = Length((res, 'px'))
                    res = res.math(arg, op)
                else:
                    break
            except StopIteration:
                op = False
        return res


class Mixin(Empty):
    """ @mixin class.
    """

    def __init__(self, t, s=None):
        super(Mixin, self).__init__(t, s)
        s.mixctx[t[0]] = self

    def include(self, target, params):
        test = map(lambda x, y: (x, y), getattr(self, 'mixinparam', []), params)
        ctx = dict(( mp.name, v or mp.default ) for mp, v in test if mp)

        if not isinstance(target, Mixin):
            for e in self.t:
                if isinstance(e, Node):
                    node = e.copy(ctx)
                    node.parse(target)


class Include(Node):
    """ @include class.
    """

    def __init__(self, t, s):
        super(Include, self).__init__(t, s)
        self.mixin = s.mixctx.get(t[0])
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
        rulesets = self.stylecheet.rset.get(name)
        if rulesets:
            for rul in rulesets:
                for sg in target.selectorgroup:
                    rul.selectorgroup.append(sg.increase(rul.selectorgroup[0]))


class Function(Node):

    def enumerate(self, p):
        return ', '.join("%s%d" % (p[0], x) for x in xrange(int(float(p[1])), int(float(p[2])+1)))

    def copy(self, ctx=None):
        return self.__parse(ctx)

    def __parse(self, ctx=dict()):
        name, params = self.t
        if hasattr(self, name):
            try:
                return getattr(self, name)(self.__parse_params(params, ctx))
            except AttributeError:
                pass
        return "%s(%s)" % (name, params)

    def __parse_params(self, params, ctx=dict()):
        result = []
        for p in map(lambda x: x.strip(), params.split(',')):
            p = p.strip('"\'')
            if p.startswith('$'):
                name = p[1:]
                p = ctx.get(name) or self.stylecheet.get_var(name) or '0'
                if not isinstance(p, str):
                    p = p.value
            result.append(p)
        return result

    def __str__(self):
        return self.__parse()


class IfNode(Node):

    def __init__(self, t, s):
        super(IfNode, self).__init__(t, s)
        self.cond, self.body, self.els = self.t

    def __str__(self):
        node = self.get_node()
        if node:
            return str(node)
        return ''

    def get_node(self):
        self.cond = self.cond.safe_str()
        ctest = self.cond.strip("'")
        if ctest.isdigit():
            return self.body if int(ctest) else self.els
        elif ctest.lower() == 'false':
            return self.els
        else:
            try:
                return self.body if eval(self.cond) else self.els
            except SyntaxError:
                return self.els

    def parse(self, target):
        node = self.get_node()
        if node:
            for n in node.t:
                n.parse(target)


class ForNode(Node):
    def __init__(self, t, s):
        super(ForNode, self).__init__(t, s)
        self.var, self.first, self.second, self.body = self.t

    def copy(self, ctx=None):
        return self

    def __parse(self):
        name = self.var.t[1]
        for i in xrange(int(self.first), int(self.second)+1):
            yield self.body.copy({name: i})

    def __str__(self):
        return ''.join(str(n) for n in self.__parse())

    def parse(self, target):
        for node in self.__parse():
            for n in node.t:
                if not isinstance(n, str):
                    n.parse(target)
