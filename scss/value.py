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


hex2rgba = {
    8: lambda c: (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), int(c[6:8], 16)),
    6: lambda c: (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), 1.0),
    4: lambda c: (int(c[0]*2, 16), int(c[1]*2, 16), int(c[2]*2, 16), int(c[3]*2, 16)),
    3: lambda c: (int(c[0]*2, 16), int(c[1]*2, 16), int(c[2]*2, 16), 1.0),
}


class ColorValue(Value):

    def __init__(self, t):
        super(ColorValue, self).__init__()

        if t is None:
            self.value = (0, 0, 0, 1)

        elif isinstance(t, (list, tuple)):
            c = t[:4]
            r = 255.0, 255.0, 255.0, 1.0
            c = [ 0.0 if c[i] < 0 else r[i] if c[i] > r[i] else c[i] for i in range(4) ]
            self.value = tuple(c)

        else:
            val = t[0]
            self.value = hex2rgba[len(val)](val)

    def __str__(self):
        if self.value[3] == 1:
            v = '%02x%02x%02x' % self.value[:3]
            if v[0] == v[1] and v[2] == v[3] and v[4] == v[5]:
                v = v[0] + v[2] + v[4]
            return '#%s' % v
        return 'rgba(%d,%d,%d,%.2f)' % self.value

    @classmethod
    def _do_op(cls, self, other, op):
        if isinstance(other, ColorValue):
            res = map(
                    lambda x, y: max(min(255, op(x, y)), 0),
                    self.value,
                    other.value)
            res[3] = 1.0

        elif isinstance(other, NumberValue):
            a = colorsys.rgb_to_hsv(*self.value[:3])
            br = op(a[2], (a[2] * float(other)))
            res = colorsys.hsv_to_rgb(a[0], a[1], br)
            res = res + ( 1.0, )

        else:
            return self

        return cls(res)


class NumberValue(Value):

    def __init__(self, t):
        super(NumberValue, self).__init__()
        if t is None:
            self.value, self.units = 0.0, ''
        elif isinstance(t, (int, float, str)):
            self.value, self.units = float(t), ''
        elif isinstance(t, NumberValue):
            self.value, self.units = t.value, t.units
        else:
            self.value, self.units = t
            self.value = float(self.value)

    def __float__(self):
        return self.value / 100.0 if self.units == '%' else self.value

    def __str__(self):
        value = ("%0.03f" % self.value).strip('0').rstrip('.') or 0
        return "%s%s" % (value, self.units)

    @classmethod
    def _do_op(cls, self, other, op):
        value = op(float(self), float(other))
        if self.units == '%':
            value = value * 100.0
        return cls((value, self.units or other.units))


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
        if hasattr(self.value, 'copy'):
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
                return NumberValue(value)
            return StringValue((value,))
        if isinstance(value, int):
            return NumberValue(value)
        return value

    @property
    def value(self):

        for n in self.data:
            if isinstance(n, Variable):
                n.ctx = self.ctx

        if len(self.data) == 1:
            return self.data[0]

        if FNCT.get(self.data[0], None):
            self.data.insert(0, NumberValue(0))

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
