class Node(object):
    """ Base node for scss objects.
    """
    delim = ' '

    def __init__(self, t, s=None):
        self.t = list(t)
        self.stylecheet = s
        for e in self.t:
            if isinstance(e, Node):
                e.parse(self)

    def parse(self, target):
        name = self.__class__.__name__.lower()
        if not hasattr(target, name):
            setattr(target, name, list())
        getattr(target, name).append(self)

    def copy(self, ctx=None):
        result = []
        for e in self.t:
            if isinstance(e, Node):
                e = e.copy(ctx)
                if hasattr(e, '__iter__'):
                    result += e
                    continue
            result.append(e)

        return self.__class__(result, self.stylecheet)

    def __str__(self):
        return self.delim.join(str(e) for e in self.t)

    def safe_str(self):
        return self.delim.join(
            (e if not e.isalnum() else "'%s'" % e) if isinstance(e, str) else "'%s'" % str(e) for e in self.t)


class Empty(Node):
    def __str__(self):
        return ''


class SimpleNode(Node):
    delim = ''
