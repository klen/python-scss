import colorsys
import operator


FNCT = {
    '^': operator.__pow__,
    '+': operator.__add__,
    '-': operator.__sub__,
    '*': operator.__mul__,
    '/': operator.__div__,
    '!': operator.__neg__,
}

class Value(object):
    def __init__(self, t):
        self.value, self.units = t
    def math(self, other, op):
        op = FNCT[op]
        return op(self, other)
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


class Color(Value):

    def __init__(self, t):
        super(Color, self).__init__(t)
        self.units, self.value = self.value, self.units
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
        if isinstance(other, Color):
            res = map(
                lambda x, y: max(min(255, op(x, y)), 0),
                self.hex_to_rgb(self.value),
                self.hex_to_rgb(other.value))
            res = self.rgb_to_hex(*res)

        elif isinstance(other, Length):
            a = self.hex_to_hsv(self.value)
            br = op(a[2], (a[2] * other.value))
            res = colorsys.hsv_to_rgb(a[0], a[1], br)
            res = self.rgb_to_hex(*map(
                lambda x: min(x*256, 255), res))

        else:
            return self

        return cls(('#', res))


class Length(Value):

    def __init__(self, t):
        super(Length, self).__init__(t)
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


class StrValue(Value):

    def __init__(self, t):
        self.value = t[0].strip('\'"')

    def __str__(self):
        return "'%s'" % self.value

    @classmethod
    def _do_op(cls, self, other, op):
        return cls((op(self.value, str(other).strip("'")),))
