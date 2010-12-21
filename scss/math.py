class Hexcolor(object):
    def __init__(self, t):
        self.value = t[1]
        if len(self.value) == 3:
            self.value = ''.join(v*2 for v in self.value)

    def __str__(self):
        v = self.value
        if v[0] == v[1] and v[2] == v[3] and v[4] == v[5]:
            v = ''.join((v[0], v[2], v[4]))
        return "#%s" % v

    @staticmethod
    def rgb_to_hex(*rgb):
        return '%02x%02x%02x' % rgb

    @staticmethod
    def hex_to_rgb(h):
        lv = len(h)
        return tuple(int(h[i:i+lv/3], 16) for i in range(0, lv, lv/3))

    def math(self, other, op):
        a = self.hex_to_rgb(self.value)
        b = self.parse(other)
        if b:
            res = list()
            for k, v in zip(a, b):
                r = max(min(256, eval(str(k) + op + str(v))), 0)
                res.append(r)
            res = self.rgb_to_hex(*res)
            return Hexcolor(('#', res))
        return self

    def parse(self, other):
        if not isinstance(other, Hexcolor):
            return False
        return self.hex_to_rgb(other.value)


class Length(object):
    def __init__(self, t):
        self.value, self.units = t

    def __str__(self):
        return "%s%s" % (self.value, self.units)

    def math(self, other, op):
        a = self.value
        b = self.parse(other)
        if b:
            try:
                res = str(eval(a + op + b))
                return Length((res, self.units))
            except SyntaxError:
                pass
        return self

    def parse(self, other):
        if isinstance(other, str):
            return other
        elif isinstance(other, Length):
            return other.value
        return False
