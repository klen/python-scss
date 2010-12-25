from scss.base import Node


class Function(Node):

    def enumerate(self, p):
        return ', '.join("%s%d" % (p[0], x) for x in xrange(int(p[1]), int(p[2])+1))

    def copy(self, ctx):
        return self.__parse(ctx)

    def __parse(self, ctx=dict()):
        name, params = self.t
        if hasattr(self, name):
            try:
                return getattr(self, name)(self.__parse_params(params, ctx))
            except:
                pass
        return "%s(%s)" % (name, params)

    def __parse_params(self, params, ctx=dict()):
        result = []
        for p in map(lambda x: x.strip(), params.split(',')):
            if p.startswith('$'):
                name = p[1:]
                p = ctx.get(name) or self.stylecheet.context.get(name) or '0'
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

    def __str__(self):
        out = ''
        name = self.var.t[1]
        for i in xrange(int(self.first), int(self.second)+1):
            node = self.body.copy({name: i})
            out += str(node)
        return out

    def parse(self, target):
        name = self.var.t[1]
        for i in xrange(int(self.first), int(self.second)+1):
            node = self.body.copy({name: i})
            for n in node.t:
                if not isinstance(n, str):
                    n.parse(target)
