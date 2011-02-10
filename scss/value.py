import colorsys


class Value(object):
    def __init__(self, t):
        self.value, self.units = t


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

    def math(self, other, op):
        if isinstance(other, Color):
            res = map(
                    lambda x, y: max(min(255, eval(str(x) + op + str(y))), 0),
                    self.hex_to_rgb(self.value),
                    self.hex_to_rgb(other.value))
            res = self.rgb_to_hex(*res)
            return Color(('#', res))

        elif isinstance(other, Length):
            a = self.hex_to_hsv(self.value)
            if op == "-":
                br = a[2] - (a[2] * other.value)
            else:
                br = a[2] + (a[2] * other.value)
            res = colorsys.hsv_to_rgb(a[0], a[1], br)
            res = self.rgb_to_hex(*map(
                lambda x: min(x*256, 255), res))
            return Color(('#', res))

        return self


class Length(Value):

    def __init__(self, t):
        super(Length, self).__init__(t)
        self.value = float(self.value)
        if self.units == '%':
            self.value = self.value / 100.00

    def __float__(self):
        return self.value

    def __str__(self):
        value = float(self) * 100 if self.units == "%" else float(self)
        value = ("%0.03f" % value).strip('0').rstrip('.')
        return "%s%s" % (value, self.units)

    def math(self, other, op):
        if op  == "*":
            res = float(self) * float(other)
        elif not float(other):
            return self
        elif op == "+":
            res = float(self) + float(other)
        elif op == "-":
            res = float(self) - float(other)
        elif op == "/":
            res = float(self) / float(other)
        return Length((res, self.units))


class StrValue(Value):

    def __init__(self, t):
        self.value = t[0].strip('\'"')

    def __float__(self):
        return 0.0

    def __str__(self):
        return "'%s'" % self.value

    def math(self, other, op):
        return StrValue([ self.value + str( other ).strip("'") ])
