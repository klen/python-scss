import math
from scss.value import ColorValue

def unknown(name, *args):
    return "%s(%s)" % ( name, ', '.join(str(a) for a in args) )

def _rgb(r, g, b):
    return _rgba(r, g, b, 1.0)

def _rgba(r, g, b, a):
    return ColorValue(( float(r), float(g), float(b), float(a) ))

def _rgba2(*args):
    pass

def _enumerate(s, b, e):
    return ', '.join(
        "%s%d" % (str(s).strip("'"), x) for x in xrange(int(float(b)), int(float(e)+1))
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

def _opacify(*args):
    pass

def _transparentize(*args):
    pass

def _lighten(*args):
    pass

def _darken(*args):
    pass

def _saturate(*args):
    pass

def _desaturate(*args):
    pass

def _grayscale(*args):
    pass

def _adjust_hue(*args):
    pass

def _adjust_lightness(*args):
    pass

def _adjust_saturation(*args):
    pass

def _scale_lightness(*args):
    pass

def _scale_saturation(*args):
    pass

def _adjust_color(*args):
    pass

def _scale_color(*args):
    pass

def _change_color(*args):
    pass

def _complement(*args):
    pass

def _invert(*args):
    pass

def _mix(*args):
    pass

def _hsl(*args):
    pass

def _hsla(*args):
    pass

def _red(*args):
    pass

def _green(*args):
    pass

def _blue(*args):
    pass

def _alpha(*args):
    pass

def _hue(*args):
    pass

def _saturation(*args):
    pass

def _lightness(*args):
    pass

def _nth(*args):
    pass

def _join(*args):
    pass

def _append(*args):
    pass

def _percentage(*args):
    pass

def _unitless(*args):
    pass

def _unit(*args):
    pass

def _if(*args):
    pass

def _type_of(*args):
    pass

def _comparable(*args):
    pass

def _elements_of_type(*args):
    pass

def _quote(*args):
    pass

def _unquote(*args):
    pass

def _pi(*args):
    pass

FUNCTION = {

    # RGB Functions
    'rgb:3': _rgb,
    'rgba:2': _rgba2,
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
    'abs:1': abs,
    'round:1': round,
    'ceil:1': math.ceil,
    'floor:1': math.floor,
    'pi:0': _pi,
}
