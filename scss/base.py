class Node(object):
    """ Base node for scss objects.
    """
    delim = ''

    def __init__(self, t, s=None):
        self.data = list(t)
        self.stylecheet = s

    def parse(self, e):
        pass

    def copy(self, ctx=None):
        t = [e.copy(ctx) if isinstance(e, Node) else e for e in self.data]
        return self.__class__(t, self.stylecheet)

    def __str__(self):
        return self.delim.join(str(e) for e in self.data)


class ParseNode(Node):

    delim = ' '

    def __init__(self, t, s=None):
        super(ParseNode, self).__init__(t, s)
        for e in self.data:
            if isinstance(e, ParseNode):
                e.parse(self)

    def parse(self, e):
        name = self.__class__.__name__.lower()
        if not hasattr(e, name):
            setattr(e, name, list())
        getattr(e, name).append(self)


class Empty(Node):
    def __str__(self):
        return ''
    safe_str = __str__


class SepValString(Node):
    """ Separated value.
    """
    delim = ', '


class SimNode(Node):
    delim = ' '


class SemiNode(SimNode):
    def __str__(self):
        return super(SemiNode, self).__str__() + ';'
