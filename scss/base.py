class Node(object):
    """ Base node for css object.
    """
    delim = ' '

    def __init__(self, t, s=None):
        self.t = list(t)
        self.stylecheet = s
        self.parent = self.context = None
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
        return self.context or self.stylecheet.context

    def __str__(self):
        return self.delim.join(str(e) for e in self.t)

    def safe_str(self):
        return self.delim.join(
            (e if not e.isalnum() else "'%s'" % e) if isinstance(e, str) else "'%s'" % str(e) for e in self.t)
