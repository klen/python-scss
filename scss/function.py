from scss.base import Node

class Function(Node):

    def enumerate(self, p):
        return ', '.join("%s%d" % (p[0], x) for x in xrange(int(p[1]), int(p[2])))

    def __parse_params(self, params):
        result = []
        for p in map(lambda x: x.strip(), params.split(',')):
            if p.startswith('$'):
                name = p[1:]
                ctx = self.getContext()
                p = ctx.get(name) or '0'
            result.append(p)
        return result

    def __str__(self):
        name, params = self.t
        if hasattr(self, name):
            try:
                return getattr(self, name)(self.__parse_params(params))
            except:
                pass
        return "%s(%s)" % (name, params)

class IfNode(Node):
    def parse(self, target):
        cond, body, els = self.t
        cond = cond.safe_str()
        ctest = cond.strip("'")
        if ctest.isdigit():
            test = int(ctest)
        elif ctest.lower() == 'false':
            test = False
        else:
            try:
                test = eval(cond)
            except SyntaxError:
                test = False
        if test:
            node = body
        else:
            node = els
        for n in node.t:
            n.parse(target)
