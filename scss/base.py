from pyparsing import ParseResults


class Node(object):
    delim = ''

    def __init__(self, t, s=None):
        self.data, self.stylecheet = t, s

    def __str__(self):
        return self.delim.join(str(e) for e in self.data)


class CopyNode(Node):

    def copy(self, ctx=None):
        t = ParseResults([
            e.copy(ctx) if hasattr(e, 'copy') else e for e in self.data
        ])
        return self.__class__(t, self.stylecheet)


class ParseNode(CopyNode):

    delim = ' '

    def __init__(self, t, s=None):
        super(ParseNode, self).__init__(t, s)
        for e in self.data:
            if hasattr(e, 'parse'):
                e.parse(self)

    def parse(self, e):
        name = self.__class__.__name__.lower()
        if not hasattr(e, name):
            setattr(e, name, list())
        getattr(e, name).append(self)


class Empty(Node):
    def __str__(self):
        return ''


class SepValString(Node):
    """ Separated value.
    """
    delim = ', '


class SimpleNode(Node):
    delim = ' '


class SemiNode(SimpleNode):
    def __str__(self):
        return super(SemiNode, self).__str__() + ';\n'


class SelectorGroup(ParseNode):
    """ Part of css rule.
    """
    def increase(self, other):
        return SelectorGroup(ParseResults( list( self.data ) + other.data[1:] ))

    def __add__(self, other):
        test = str(other)
        if '&' in test:
            stest = str(self)
            return SelectorGroup(ParseResults( test.replace('&', stest).split() ))
        else:
            return SelectorGroup(self.data + other.data)


