import colorsys
import operator

from scss.base import Node


FNCT = {
    '^': operator.__pow__,
    '+': operator.__add__,
    '-': operator.__sub__,
    '*': operator.__mul__,
    '/': operator.__div__,
    '!': operator.__neg__,
}

class Value(object):
    @classmethod
    def _do_op(cls, first, second, op):
        return op(first.value, second.value)
    def __add__(self, other):
        return self._do_op(self, other, operator.__add__)
    __radd__ = __add__
    def __div__(self, other):
        return self._do_op(self, other, operator.__div__)
    def __rdiv__(self, other):
        return self._do_op(other, self, operator.__div__)
    def __sub__(self, other):
        return self._do_op(self, other, operator.__sub__)
    def __rsub__(self, other):
        return self._do_op(other, self, operator.__sub__)
    def __mul__(self, other):
        return self._do_op(self, other, operator.__mul__)
    __rmul__ = __mul__


class ColorValue(Value):

    def __init__(self, t):
        super(ColorValue, self).__init__()
        self.units, self.value = t
        if len(self.value) == 3:
            self.value = ''.join(v*2 for v in self.value)

    def __float__(self):
        return float(self.value)

    def __str__(self):
        v = self.value
        if v[0] == v[1] and v[2] == v[3] and v[4] == v[5]:
            v = ''.join((v[0], v[2], v[4]))
        return ''.join(( self.units, v ))

    @staticmethod
    def rgb_to_hex(*rgb):
        return '%02x%02x%02x' % rgb

    @staticmethod
    def hex_to_rgb(h):
        lv = len(h)
        return tuple(int(h[i:i+lv/3], 16) for i in range(0, lv, lv/3))

    @staticmethod
    def hex_to_hsv(h):
        lv = len(h)
        return colorsys.rgb_to_hsv(
            *tuple(int(h[i:i+lv/3], 16)/256.0 for i in range(0, lv, lv/3)))

    @classmethod
    def _do_op(cls, self, other, op):
        if isinstance(other, ColorValue):
            res = map(
                lambda x, y: max(min(255, op(x, y)), 0),
                self.hex_to_rgb(self.value),
                self.hex_to_rgb(other.value))
            res = self.rgb_to_hex(*res)

        elif isinstance(other, NumberValue):
            a = self.hex_to_hsv(self.value)
            br = op(a[2], (a[2] * other.value))
            res = colorsys.hsv_to_rgb(a[0], a[1], br)
            res = self.rgb_to_hex(*map(
                lambda x: min(x*256, 255), res))

        else:
            return self

        return cls(('#', res))


class NumberValue(Value):

    def __init__(self, t):
        super(NumberValue, self).__init__()
        self.value, self.units = t
        self.value = float(self.value) / 100.00 if self.units == '%' else float(self.value)

    def __float__(self):
        return self.value

    def __str__(self):
        value = ("%0.03f" % ( self.value * 100.00 if self.units == '%' else self.value )).strip('0').rstrip('.') or 0
        return "%s%s" % (value, self.units)

    @classmethod
    def _do_op(cls, self, other, op):
        value = op(float(self), float(other))
        if self.units == '%':
            value = value * 100
        return cls((value, self.units))


class StringValue(Value):

    def __init__(self, t):
        super(StringValue, self).__init__()
        self.value = t[0].strip('\'"')

    def __str__(self):
        return "'%s'" % self.value

    @classmethod
    def _do_op(cls, self, other, op):
        return cls((op(self.value, str(other).strip("'")),))


class BooleanValue(Value):

    def __init__(self, t):
        super(BooleanValue, self).__init__()
        self.value = True if t[0] == 'true' else False

    def __str__(self):
        return 'true' if self.value else 'false'


class Variable(Node, Value):
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
        """ Return variable value.
        """
        name = self.data[1]
        if self.ctx and self.ctx.get(name):
            return self.ctx.get(name)
        return self.stylecheet.get_var(name)

    def __str__(self):
        return str(self.value)

    def __float__(self):
        try:
            return float(self.value)
        except ValueError:
            return 0.0


class VarStringMeta(type):
    def __call__(mcs, *args):
        data = args[0]
        if len(data) == 1 and isinstance( data[0], ( Node, Value ) ):
            return data[0]
        return super(VarStringMeta, mcs).__call__(*args)


class VarString(Variable):
    """ Parse mathematic operation.
    """
    __metaclass__ = VarStringMeta

    @staticmethod
    def prepare(value):
        while isinstance(value, Variable):
            value = value.value
        if isinstance(value, str):
            if value.isdigit():
                return NumberValue((value, 'px'))
            return StringValue((value,))
        if isinstance(value, int):
            return NumberValue((value, 'px'))
        return value

    @property
    def value(self):

        for n in self.data:
            if isinstance(n, Variable):
                n.ctx = self.ctx

        if len(self.data) == 1:
            return self.data[0]

        if FNCT.get(self.data[0], None):
            v = self.prepare( self.data[1] )
            self.data.insert(0, NumberValue((0, v.units)))

        it = iter(self.data)
        first, res = next(it), next(it)
        while True:
            try:
                op = FNCT.get(res, None)
                if op:
                    second = next(it)
                    first = op(self.prepare( first ), self.prepare( second ))
                res = next(it)
            except StopIteration:
                break
        return first
