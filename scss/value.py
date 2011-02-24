import colorsys

from scss import OPRT, CONV_FACTOR, COLORS
from scss.base import Node

class Value(object):
    @classmethod
    def _do_op(cls, first, second, op):
        return op(first.value, second.value)
    @classmethod
    def _do_cmps(cls, first, second, op):
        return op(first.value, second.value)
    @classmethod
    def _do_bits(cls, first, second, op):
        first = StringValue(first)
        second = StringValue(second)
        k = op(first.value, second.value)
        return first if first.value == k else second

    # Math operation
    def __add__(self, other):
        return self._do_op(self, other, OPRT['+'])
    __radd__ = __add__
    def __div__(self, other):
        return self._do_op(self, other, OPRT['/'])
    def __rdiv__(self, other):
        return self._do_op(other, self, OPRT['/'])
    def __sub__(self, other):
        return self._do_op(self, other, OPRT['-'])
    def __rsub__(self, other):
        return self._do_op(other, self, OPRT['-'])
    def __mul__(self, other):
        return self._do_op(self, other, OPRT['*'])
    def __lt__(self, other):
        return self._do_cmps(self, other, OPRT['<'])
    __rmul__ = __mul__

    # Compare operation
    def __le__(self, other):
        return self._do_cmps(self, other, OPRT['<='])
    def __gt__(self, other):
        return self._do_cmps(self, other, OPRT['>='])
    def __ge__(self, other):
        return self._do_cmps(self, other, OPRT['>'])
    def __eq__(self, other):
        return self._do_cmps(self, other, OPRT['=='])
    def __ne__(self, other):
        return self._do_cmps(self, other, OPRT['!='])

    # Bit operation
    def __and__(self, other):
        return self._do_bits(self, other, OPRT['and'])
    def __or__(self, other):
        return self._do_bits(self, other, OPRT['or'])

    # Boolean
    def __nonzero__(self):
        return getattr(self, 'value') and True or False


hex2rgba = {
    8: lambda c: (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), int(c[6:8], 16)),
    6: lambda c: (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), 1.0),
    4: lambda c: (int(c[0]*2, 16), int(c[1]*2, 16), int(c[2]*2, 16), int(c[3]*2, 16)),
    3: lambda c: (int(c[0]*2, 16), int(c[1]*2, 16), int(c[2]*2, 16), 1.0),
}


def hsl_op(op, color, h, s, l):
    other = (float(h), float(l), float(s))
    self = colorsys.rgb_to_hls(*map(lambda x: x / 255.0, color.value[:3]))
    res = colorsys.hls_to_rgb(*map(lambda x, y: op(x, y) if op else y if y else x, self, other))
    return ColorValue(( res[0] * 255.0, res[1] * 255.0, res[2] * 255.0, color.value[3] ))


def rgba_op(op, color, r, g, b, a):
    other = (float(r), float(g), float(b), float(a))
    res = ColorValue(map(lambda x, y: op(x, y) if op else y if y else x, color.value, other))
    if float(a) == color.value[3] == 1:
        res.value = (res.value[0], res.value[1], res.value[2], 1.0)
    return res


class ColorValue(Value):

    def __init__(self, t):
        super(ColorValue, self).__init__()

        if t is None:
            self.value = (0, 0, 0, 1)

        elif isinstance(t, str):
            val = t[1:]
            self.value = hex2rgba[len(val)](val)

        elif isinstance(t, (list, tuple)):
            if len(t) < 4:
                c = (t[0], t[1], t[2], 1.0)
            else:
                c = t[:4]
            r = 255.0, 255.0, 255.0, 1.0
            c = [ 0.0 if c[i] < 0 else r[i] if c[i] > r[i] else c[i] for i in range(4) ]
            self.value = tuple(c)

        else:
            val = t[0][1:]
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
            return rgba_op(op, self, *other.value)

        elif isinstance(other, NumberValue):
            val = float(other)
            if op in (OPRT['*'], OPRT['/']):
                return ColorValue(map(lambda x: op(x, val), self.value[:3]))
            return hsl_op(op, self, 0, val, 0)

        else:
            return self


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
            self.value, self.units = t[0], str(t[1]) if len(t) > 1 else ''
            self.value = float(self.value)

    def __float__(self):
        return self.value * CONV_FACTOR.get(self.units, 1.0)

    def __str__(self):
        value = ("%0.03f" % self.value).strip('0').rstrip('.') or 0
        return "%s%s" % (value, self.units if self.value else '')

    @classmethod
    def _do_op(cls, self, other, op):
        value = op(float(self), float(other))
        value /= CONV_FACTOR.get(self.units or other.units, 1.0)

        return cls((value, self.units or other.units))


class StringValue(Value):

    def __init__(self, t):
        super(StringValue, self).__init__()
        if isinstance(t, ( str, int, float, NumberValue )):
            self.value = str(t)
        elif isinstance(t, StringValue):
            self.value = t.value
        else:
            self.value = str(t[0]).strip('\'"')

    def __str__(self):
        return "%s" % self.value

    @classmethod
    def _do_op(cls, self, other, op):
        return cls(op(self.value, str(other).strip("'")))


class QuotedStringValue(StringValue):

    def __str__(self):
        return "'%s'" % self.value


class BooleanValue(Value):

    def __init__(self, t):
        super(BooleanValue, self).__init__()
        if t is None:
            self.value = False
        elif isinstance(t, Value):
            self.value = bool(t.value) if t.value != 'false' else False
        elif isinstance(t, ( str, bool )):
            self.value = bool(t) if t != 'false' else False
        else:
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
        name = self.data[0].lstrip('$-')
        if self.ctx and self.ctx.get(name):
            value = self.ctx.get(name)
        else:
            value = self.root.get_var(name)
        return (self.root.defvalue - value) if self.data[0][0] == '-' else value

    def __str__(self):
        return str(self.value)

    def __float__(self):
        try:
            return float(self.value)
        except ValueError:
            return 0.0


class ExpressionMeta(type):
    def __call__(mcs, *args):
        data = args[0]
        if len(data) == 1:
            return data[0]
        return super(ExpressionMeta, mcs).__call__(*args)

class Expression(Variable):
    """ Parse mathematic operation.
    """
    __metaclass__ = ExpressionMeta

    @staticmethod
    def prepare(value):
        while isinstance(value, Variable):
            value = value.value
        if isinstance(value, str):
            value = ColorValue(COLORS[value]) if COLORS.has_key(value) else StringValue(value)
        return value

    @property
    def value(self):
        return self.do_expression(self.data, self.ctx)

    @classmethod
    def do_expression(cls, data, ctx=None):

        if ctx:
            for n in data:
                if isinstance(n, Variable):
                    n.ctx = ctx

        it = iter(data)
        first, res = next(it), next(it)
        while True:
            try:
                op = OPRT.get(res, None)
                if op:
                    second = next(it)
                    first = op(cls.prepare( first ), cls.prepare( second ))

                    if op == OPRT['and'] and not first:
                        raise StopIteration

                    elif op == OPRT['or'] and first:
                        raise StopIteration

                res = next(it)
            except StopIteration:
                break
        return first

