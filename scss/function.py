import colorsys
import math

from scss import OPRT, CONV_TYPE
from scss.value import ColorValue, NumberValue, hsl_op, rgba_op, StringValue, QuotedStringValue, BooleanValue


def unknown(name, *args):
    return "%s(%s)" % ( name, ', '.join(str(a) for a in args) )


# RGB functions
# =============

def _rgb(r, g, b):
    """ Converts an rgb(red, green, blue) triplet into a color.
    """
    return _rgba(r, g, b, 1.0)

def _rgba(r, g, b, a):
    """ Converts an rgba(red, green, blue, alpha) quadruplet into a color.
    """
    return ColorValue(( float(r), float(g), float(b), float(a) ))

def _red(color):
    """ Gets the red component of a color.
    """
    return NumberValue(color.value[0])

def _green(color):
    """ Gets the green component of a color.
    """
    return NumberValue(color.value[1])

def _blue(color):
    """ Gets the blue component of a color.
    """
    return NumberValue(color.value[2])

def _mix(color1, color2, weight=0.5):
    """ Mixes two colors together.
    """
    weight = float(weight)
    c1 = color1.value
    c2 = color2.value
    p = 0.0 if weight < 0 else 1.0 if weight > 1 else weight
    w = p * 2 - 1
    a = c1[3] - c2[3]

    w1 = ((w if (w * a == -1) else (w + a) / (1 + w * a)) + 1) / 2.0
    w2 = 1 - w1
    q = [ w1, w1, w1, p ]
    r = [ w2, w2, w2, 1 - p ]
    return ColorValue([ c1[i] * q[i] + c2[i] * r[i] for i in range(4) ])


# HSL functions
# =============

def _hsl(h, s, l):
    return _hsla(h, s, l, 1.0)

def _hsla(h, s, l, a):
    res = colorsys.hls_to_rgb(float(h), float(l), float(s))
    return ColorValue(map( lambda x: x * 255.0, res ) + list((a,)))

def _hue(color):
    h = colorsys.rgb_to_hls( *map(lambda x: x / 255.0, color.value[:3]) )[0]
    return NumberValue(h * 360.0)

def _saturation(color):
    s = colorsys.rgb_to_hls( *map(lambda x: x / 255.0, color.value[:3]) )[2]
    return NumberValue(s * 255.0)

def _lightness(color):
    l = colorsys.rgb_to_hls( *map(lambda x: x / 255.0, color.value[:3]) )[1]
    return NumberValue(l * 255.0)

def _adjust_hue(color, degrees):
    return hsl_op(OPRT['+'], color, degrees, 0, 0)

def _lighten(color, amount):
    return hsl_op(OPRT['+'], color, 0, 0, amount)

def _darken(color, amount):
    return hsl_op(OPRT['-'], color, 0, 0, amount)

def _saturate(color, amount):
    return hsl_op(OPRT['+'], color, 0, amount, 0)

def _desaturate(color, amount):
    return hsl_op(OPRT['-'], color, 0, amount, 0)

def _grayscale(color):
    return hsl_op(OPRT['-'], color, 0, 1.0, 0)

def _complement(color):
    return hsl_op(OPRT['+'], color, 180.0, 0, 0)


# Opacity functions
# =================

def _alpha(color):
    c = ColorValue(color).value
    return NumberValue(c[3])

def _opacify(color, amount):
    return rgba_op(OPRT['+'], color, 0, 0, 0, amount)

def _transparentize(color, amount):
    return rgba_op(OPRT['-'], color, 0, 0, 0, amount)


# String functions
# =================

def _unquote(*args):
    return StringValue(' '.join(str(s).strip("\"'") for s in args))

def _quote(*args):
    return QuotedStringValue(' '.join(str(s) for s in args))


# Number functions
# =================

def _percentage(value):
    value = NumberValue(value)
    if not value.units == '%':
        value.value *= 100
        value.units = '%'
    return value

def _abs(value):
    return abs(float(value))

def _pi():
    return NumberValue(math.pi)


# Introspection functions
# =======================

def _type_of(obj):
    if isinstance(obj, BooleanValue):
        return StringValue('bool')
    if isinstance(obj, NumberValue):
        return StringValue('number')
    if isinstance(obj, QuotedStringValue):
        return StringValue('string')
    if isinstance(obj, ColorValue):
        return StringValue('color')
    if isinstance(obj, dict):
        return StringValue('list')
    return 'unknown'

def _unit(value):
    return NumberValue(value).units

def _unitless(value):
    if NumberValue(value).units:
        return BooleanValue(False)
    return BooleanValue(True)

def _comparable(n1, n2):
    n1, n2 = NumberValue(n1), NumberValue(n2)
    type1 = CONV_TYPE.get(n1.units)
    type2 = CONV_TYPE.get(n2.units)
    return BooleanValue(type1 == type2)


# Color functions
# ================

def _adjust_color(color, saturation=None, lightness=None, red=None, green=None, blue=None, alpha=None):
    return _asc_color(OPRT['+'], color, saturation, lightness, red, green, blue, alpha)

def _scale_color(color, saturation=None, lightness=None, red=None, green=None, blue=None, alpha=None):
    return _asc_color(OPRT['*'], color, saturation, lightness, red, green, blue, alpha)

def _change_color(color, saturation=None, lightness=None, red=None, green=None, blue=None, alpha=None):
    return _asc_color(None, color, saturation, lightness, red, green, blue, alpha)




def _enumerate(s, b, e):
    return ', '.join(
        "%s%d" % (StringValue(s).value, x) for x in xrange(int(b.value), int(e.value+1))
    )

def _sprite_position(*args):
    pass

def _sprite_file(*args):
    pass

def _sprite(*args):
    pass

def _sprite_map(*args):
    pass

def _sprite_map_name(*args):
    pass

def _sprite_url(*args):
    pass

def _inline_image(*args):
    pass

def _image_url(*args):
    pass

def _image_width(*args):
    pass

def _image_height(*args):
    pass

def _opposite_position(*args):
    pass

def _grad_point(*args):
    pass

def _color_stops(*args):
    pass

def _grad_color_stops(*args):
    pass

def _adjust_lightness(*args):
    pass

def _adjust_saturation(*args):
    pass

def _scale_lightness(*args):
    pass

def _scale_saturation(*args):
    pass

def _invert(*args):
    pass

def _nth(*args):
    pass

def _join(*args):
    pass

def _append(*args):
    pass

def _if(*args):
    pass

def _elements_of_type(*args):
    pass

FUNCTION = {

    # RGB Functions
    'rgb:3': _rgb,
    'rgba:4': _rgba,
    'red:1': _red,
    'green:1': _green,
    'blue:1': _blue,
    'mix:2': _mix,
    'mix:3': _mix,

    'sprite-map:1': _sprite_map,
    'sprite:2': _sprite,
    'sprite:3': _sprite,
    'sprite:4': _sprite,
    'sprite-map-name:1': _sprite_map_name,
    'sprite-file:2': _sprite_file,
    'sprite-url:1': _sprite_url,
    'sprite-position:2': _sprite_position,
    'sprite-position:3': _sprite_position,
    'sprite-position:4': _sprite_position,

    'inline-image:1': _inline_image,
    'inline-image:2': _inline_image,
    'image-url:1': _image_url,
    'image-width:1': _image_width,
    'image-height:1': _image_height,

    'opposite-position:n': _opposite_position,
    'grad-point:n': _grad_point,
    'color-stops:n': _color_stops,
    'grad-color-stops:n': _grad_color_stops,

    'opacify:2': _opacify,
    'fadein:2': _opacify,
    'fade-in:2': _opacify,
    'transparentize:2': _transparentize,
    'fadeout:2': _transparentize,
    'fade-out:2': _transparentize,
    'lighten:2': _lighten,
    'darken:2': _darken,
    'saturate:2': _saturate,
    'desaturate:2': _desaturate,
    'grayscale:1': _grayscale,
    'adjust-hue:2': _adjust_hue,
    'adjust-lightness:2': _adjust_lightness,
    'adjust-saturation:2': _adjust_saturation,
    'scale-lightness:2': _scale_lightness,
    'scale-saturation:2': _scale_saturation,
    'adjust-color:n': _adjust_color,
    'scale-color:n': _scale_color,
    'change-color:n': _change_color,
    'spin:2': _adjust_hue,
    'complement:1': _complement,
    'invert:1': _invert,
    'hsl:3': _hsl,
    'hsla:4': _hsla,

    'alpha:1': _alpha,
    'opacity:1': _alpha,
    'hue:1': _hue,
    'saturation:1': _saturation,
    'lightness:1': _lightness,

    'nth:2': _nth,
    'first-value-of:1': _nth,
    'join:2': _join,
    'join:3': _join,
    'append:2': _append,
    'append:3': _append,

    'enumerate:3': _enumerate,
    'percentage:1': _percentage,
    'unitless:1': _unitless,
    'unit:1': _unit,
    'if:3': _if,
    'type-of:1': _type_of,
    'comparable:2': _comparable,
    'elements-of-type:1': _elements_of_type,
    'quote:n': _quote,
    'unquote:n': _unquote,
    'escape:1': _unquote,
    'e:1': _unquote,

    'sin:1': math.sin,
    'cos:1': math.cos,
    'tan:1': math.tan,
    'abs:1': _abs,
    'round:1': round,
    'ceil:1': math.ceil,
    'floor:1': math.floor,
    'pi:0': _pi,
}

def _asc_color(op, color, saturation=None, lightness=None, red=None, green=None, blue=None, alpha=None):
    if lightness or saturation:
        color = hsl_op(op, color, 0, saturation, lightness)
    if red or green or blue or alpha:
        color = rgba_op(op, color, red, green, blue, alpha)
    return color
