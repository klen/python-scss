class Node(object):
    """ Base node for scss objects.
    """
    delim = ' '

    def __init__(self, t, s=None):
        self.data = list(t)
        self.stylecheet = s
        for e in self.data:
            if isinstance(e, Node):
                e.parse(self)

    def parse(self, e):
        name = self.__class__.__name__.lower()
        if not hasattr(e, name):
            setattr(e, name, list())
        getattr(e, name).append(self)

    def copy(self, ctx=None):
        t = [e.copy(ctx) if isinstance(e, Node) else e for e in self.data]
        return self.__class__(t, self.stylecheet)

    def __str__(self):
        return self.delim.join(str(e) for e in self.data)

    def safe_str(self):
        return self.delim.join(
            (e if not e.isalnum() else "'%s'" % e) if isinstance(e, str) else "'%s'" % str(e) for e in self.data)


class Empty(Node):
    def parse(self, e):
        pass
    def __str__(self):
        return ''
    safe_str = __str__


class SimpleNode(Node):
    delim = ''
