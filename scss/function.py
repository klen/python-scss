from scss.base import Node, Empty, ParseNode
from scss.grammar import VAL_STRING
from scss.value import Color, Variable


class VarDef(Empty):
    """ Variable definition.
    """
    def __init__(self, t, s):
        super(VarDef, self).__init__(t, s)
        name, self.value, default = t
        default = not isinstance(default, Empty)
        s.set_var(name, self.value, default)

    def copy(self, ctx=None):
        self.value.ctx = ctx
        return self


class SepValString(Node):
    """ Separated value.
    """
    delim = ', '


class Mixin(ParseNode):
    """ @mixin class.
    """

    def __init__(self, t, s=None):
        super(Mixin, self).__init__(t, s)
        s.mixctx[t[0]] = self

    def include(self, target, params):
        test = map(lambda x, y: (x, y), getattr(self, 'mixinparam', []), params)
        ctx = dict(( mp.name, v or mp.default ) for mp, v in test if mp)

        if not isinstance(target, Mixin):
            for e in self.data:
                if isinstance(e, Node):
                    node = e.copy(ctx)
                    node.parse(target)

    def __str__(self):
        return ''



class Include(ParseNode):
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
        self.name, params = self.data
        self.params = [p[0][0] for p in VAL_STRING.scanString(params)]

    def enumerate(self, pm):
        return ', '.join("%s%d" % (str( pm[0] ).strip("'"), x) for x in xrange(int(float(pm[1])), int(float(pm[2])+1)))

    def rgb(self, pm):
        return Color(( '#', ''.join('%x' % int(float(x)) for x in pm) ))

    def rgba(self, pm):
        return 'rgba(%s)' % ', '.join(str(p) for p in pm)

    @property
    def value(self):
        return self.__parse(self.ctx)

    def copy(self, ctx=None):
        return self.__parse(ctx)

    def __parse(self, ctx=dict()):
        if hasattr(self, self.name):
            return getattr(self, self.name)(self.params)
        params = ''.join(str(p) for p in self.params)
        return "%s(%s)" % (self.name, params)

    def __str__(self):
        return str(self.__parse())


class IfNode(ParseNode):

    def __init__(self, t, s):
        super(IfNode, self).__init__(t, s)
        self.cond, self.body, self.els = self.data

    def __str__(self):
        node = self.get_node()
        if node:
            return str(node)
        return ''

    def get_node(self):
        cond = self.cond.delim.join(
            (e if not e.isalnum() else "'%s'" % e) if isinstance(e, str) else "'%s'" % str(e) for e in self.cond.data)
        ctest = cond.strip("'")
        if ctest.isdigit():
            return self.body if int(ctest) else self.els
        elif ctest.lower() == 'false':
            return self.els
        else:
            try:
                return self.body if eval(cond) else self.els
            except SyntaxError:
                return self.els

    def parse(self, target):
        node = self.get_node()
        if node:
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
            yield self.body.copy({name: i})

    def __str__(self):
        return ''.join(str(n) for n in self.__parse())

    def parse(self, target):
        for node in self.__parse():
            for n in node.data:
                if not isinstance(n, str):
                    n.parse(target)
