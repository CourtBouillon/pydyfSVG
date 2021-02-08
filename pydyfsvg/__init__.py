import re
from xml.etree import ElementTree


INVISIBLE_TAGS = (
    'clipPath', 'filter', 'linearGradient', 'marker', 'mask', 'pattern',
    'radialGradient', 'symbol')


UNITS = {
    'mm': 1 / 25.4,
    'cm': 1 / 2.54,
    'in': 1,
    'pt': 1 / 72.,
    'pc': 1 / 6.,
    'px': None,
}


COLORS = {
    'aliceblue': (240 / 255, 248 / 255, 255 / 255, 1),
    'antiquewhite': (250 / 255, 235 / 255, 215 / 255, 1),
    'aqua': (0 / 255, 255 / 255, 255 / 255, 1),
    'aquamarine': (127 / 255, 255 / 255, 212 / 255, 1),
    'azure': (240 / 255, 255 / 255, 255 / 255, 1),
    'beige': (245 / 255, 245 / 255, 220 / 255, 1),
    'bisque': (255 / 255, 228 / 255, 196 / 255, 1),
    'black': (0 / 255, 0 / 255, 0 / 255, 1),
    'blanchedalmond': (255 / 255, 235 / 255, 205 / 255, 1),
    'blue': (0 / 255, 0 / 255, 255 / 255, 1),
    'blueviolet': (138 / 255, 43 / 255, 226 / 255, 1),
    'brown': (165 / 255, 42 / 255, 42 / 255, 1),
    'burlywood': (222 / 255, 184 / 255, 135 / 255, 1),
    'cadetblue': (95 / 255, 158 / 255, 160 / 255, 1),
    'chartreuse': (127 / 255, 255 / 255, 0 / 255, 1),
    'chocolate': (210 / 255, 105 / 255, 30 / 255, 1),
    'coral': (255 / 255, 127 / 255, 80 / 255, 1),
    'cornflowerblue': (100 / 255, 149 / 255, 237 / 255, 1),
    'cornsilk': (255 / 255, 248 / 255, 220 / 255, 1),
    'crimson': (220 / 255, 20 / 255, 60 / 255, 1),
    'cyan': (0 / 255, 255 / 255, 255 / 255, 1),
    'darkblue': (0 / 255, 0 / 255, 139 / 255, 1),
    'darkcyan': (0 / 255, 139 / 255, 139 / 255, 1),
    'darkgoldenrod': (184 / 255, 134 / 255, 11 / 255, 1),
    'darkgray': (169 / 255, 169 / 255, 169 / 255, 1),
    'darkgreen': (0 / 255, 100 / 255, 0 / 255, 1),
    'darkgrey': (169 / 255, 169 / 255, 169 / 255, 1),
    'darkkhaki': (189 / 255, 183 / 255, 107 / 255, 1),
    'darkmagenta': (139 / 255, 0 / 255, 139 / 255, 1),
    'darkolivegreen': (85 / 255, 107 / 255, 47 / 255, 1),
    'darkorange': (255 / 255, 140 / 255, 0 / 255, 1),
    'darkorchid': (153 / 255, 50 / 255, 204 / 255, 1),
    'darkred': (139 / 255, 0 / 255, 0 / 255, 1),
    'darksalmon': (233 / 255, 150 / 255, 122 / 255, 1),
    'darkseagreen': (143 / 255, 188 / 255, 143 / 255, 1),
    'darkslateblue': (72 / 255, 61 / 255, 139 / 255, 1),
    'darkslategray': (47 / 255, 79 / 255, 79 / 255, 1),
    'darkslategrey': (47 / 255, 79 / 255, 79 / 255, 1),
    'darkturquoise': (0 / 255, 206 / 255, 209 / 255, 1),
    'darkviolet': (148 / 255, 0 / 255, 211 / 255, 1),
    'deeppink': (255 / 255, 20 / 255, 147 / 255, 1),
    'deepskyblue': (0 / 255, 191 / 255, 255 / 255, 1),
    'dimgray': (105 / 255, 105 / 255, 105 / 255, 1),
    'dimgrey': (105 / 255, 105 / 255, 105 / 255, 1),
    'dodgerblue': (30 / 255, 144 / 255, 255 / 255, 1),
    'firebrick': (178 / 255, 34 / 255, 34 / 255, 1),
    'floralwhite': (255 / 255, 250 / 255, 240 / 255, 1),
    'forestgreen': (34 / 255, 139 / 255, 34 / 255, 1),
    'fuchsia': (255 / 255, 0 / 255, 255 / 255, 1),
    'gainsboro': (220 / 255, 220 / 255, 220 / 255, 1),
    'ghostwhite': (248 / 255, 248 / 255, 255 / 255, 1),
    'gold': (255 / 255, 215 / 255, 0 / 255, 1),
    'goldenrod': (218 / 255, 165 / 255, 32 / 255, 1),
    'gray': (128 / 255, 128 / 255, 128 / 255, 1),
    'grey': (128 / 255, 128 / 255, 128 / 255, 1),
    'green': (0 / 255, 128 / 255, 0 / 255, 1),
    'greenyellow': (173 / 255, 255 / 255, 47 / 255, 1),
    'honeydew': (240 / 255, 255 / 255, 240 / 255, 1),
    'hotpink': (255 / 255, 105 / 255, 180 / 255, 1),
    'indianred': (205 / 255, 92 / 255, 92 / 255, 1),
    'indigo': (75 / 255, 0 / 255, 130 / 255, 1),
    'ivory': (255 / 255, 255 / 255, 240 / 255, 1),
    'khaki': (240 / 255, 230 / 255, 140 / 255, 1),
    'lavender': (230 / 255, 230 / 255, 250 / 255, 1),
    'lavenderblush': (255 / 255, 240 / 255, 245 / 255, 1),
    'lawngreen': (124 / 255, 252 / 255, 0 / 255, 1),
    'lemonchiffon': (255 / 255, 250 / 255, 205 / 255, 1),
    'lightblue': (173 / 255, 216 / 255, 230 / 255, 1),
    'lightcoral': (240 / 255, 128 / 255, 128 / 255, 1),
    'lightcyan': (224 / 255, 255 / 255, 255 / 255, 1),
    'lightgoldenrodyellow': (250 / 255, 250 / 255, 210 / 255, 1),
    'lightgray': (211 / 255, 211 / 255, 211 / 255, 1),
    'lightgreen': (144 / 255, 238 / 255, 144 / 255, 1),
    'lightgrey': (211 / 255, 211 / 255, 211 / 255, 1),
    'lightpink': (255 / 255, 182 / 255, 193 / 255, 1),
    'lightsalmon': (255 / 255, 160 / 255, 122 / 255, 1),
    'lightseagreen': (32 / 255, 178 / 255, 170 / 255, 1),
    'lightskyblue': (135 / 255, 206 / 255, 250 / 255, 1),
    'lightslategray': (119 / 255, 136 / 255, 153 / 255, 1),
    'lightslategrey': (119 / 255, 136 / 255, 153 / 255, 1),
    'lightsteelblue': (176 / 255, 196 / 255, 222 / 255, 1),
    'lightyellow': (255 / 255, 255 / 255, 224 / 255, 1),
    'lime': (0 / 255, 255 / 255, 0 / 255, 1),
    'limegreen': (50 / 255, 205 / 255, 50 / 255, 1),
    'linen': (250 / 255, 240 / 255, 230 / 255, 1),
    'magenta': (255 / 255, 0 / 255, 255 / 255, 1),
    'maroon': (128 / 255, 0 / 255, 0 / 255, 1),
    'mediumaquamarine': (102 / 255, 205 / 255, 170 / 255, 1),
    'mediumblue': (0 / 255, 0 / 255, 205 / 255, 1),
    'mediumorchid': (186 / 255, 85 / 255, 211 / 255, 1),
    'mediumpurple': (147 / 255, 112 / 255, 219 / 255, 1),
    'mediumseagreen': (60 / 255, 179 / 255, 113 / 255, 1),
    'mediumslateblue': (123 / 255, 104 / 255, 238 / 255, 1),
    'mediumspringgreen': (0 / 255, 250 / 255, 154 / 255, 1),
    'mediumturquoise': (72 / 255, 209 / 255, 204 / 255, 1),
    'mediumvioletred': (199 / 255, 21 / 255, 133 / 255, 1),
    'midnightblue': (25 / 255, 25 / 255, 112 / 255, 1),
    'mintcream': (245 / 255, 255 / 255, 250 / 255, 1),
    'mistyrose': (255 / 255, 228 / 255, 225 / 255, 1),
    'moccasin': (255 / 255, 228 / 255, 181 / 255, 1),
    'navajowhite': (255 / 255, 222 / 255, 173 / 255, 1),
    'navy': (0 / 255, 0 / 255, 128 / 255, 1),
    'oldlace': (253 / 255, 245 / 255, 230 / 255, 1),
    'olive': (128 / 255, 128 / 255, 0 / 255, 1),
    'olivedrab': (107 / 255, 142 / 255, 35 / 255, 1),
    'orange': (255 / 255, 165 / 255, 0 / 255, 1),
    'orangered': (255 / 255, 69 / 255, 0 / 255, 1),
    'orchid': (218 / 255, 112 / 255, 214 / 255, 1),
    'palegoldenrod': (238 / 255, 232 / 255, 170 / 255, 1),
    'palegreen': (152 / 255, 251 / 255, 152 / 255, 1),
    'paleturquoise': (175 / 255, 238 / 255, 238 / 255, 1),
    'palevioletred': (219 / 255, 112 / 255, 147 / 255, 1),
    'papayawhip': (255 / 255, 239 / 255, 213 / 255, 1),
    'peachpuff': (255 / 255, 218 / 255, 185 / 255, 1),
    'peru': (205 / 255, 133 / 255, 63 / 255, 1),
    'pink': (255 / 255, 192 / 255, 203 / 255, 1),
    'plum': (221 / 255, 160 / 255, 221 / 255, 1),
    'powderblue': (176 / 255, 224 / 255, 230 / 255, 1),
    'purple': (128 / 255, 0 / 255, 128 / 255, 1),
    'red': (255 / 255, 0 / 255, 0 / 255, 1),
    'rosybrown': (188 / 255, 143 / 255, 143 / 255, 1),
    'royalblue': (65 / 255, 105 / 255, 225 / 255, 1),
    'saddlebrown': (139 / 255, 69 / 255, 19 / 255, 1),
    'salmon': (250 / 255, 128 / 255, 114 / 255, 1),
    'sandybrown': (244 / 255, 164 / 255, 96 / 255, 1),
    'seagreen': (46 / 255, 139 / 255, 87 / 255, 1),
    'seashell': (255 / 255, 245 / 255, 238 / 255, 1),
    'sienna': (160 / 255, 82 / 255, 45 / 255, 1),
    'silver': (192 / 255, 192 / 255, 192 / 255, 1),
    'skyblue': (135 / 255, 206 / 255, 235 / 255, 1),
    'slateblue': (106 / 255, 90 / 255, 205 / 255, 1),
    'slategray': (112 / 255, 128 / 255, 144 / 255, 1),
    'slategrey': (112 / 255, 128 / 255, 144 / 255, 1),
    'snow': (255 / 255, 250 / 255, 250 / 255, 1),
    'springgreen': (0 / 255, 255 / 255, 127 / 255, 1),
    'steelblue': (70 / 255, 130 / 255, 180 / 255, 1),
    'tan': (210 / 255, 180 / 255, 140 / 255, 1),
    'teal': (0 / 255, 128 / 255, 128 / 255, 1),
    'thistle': (216 / 255, 191 / 255, 216 / 255, 1),
    'tomato': (255 / 255, 99 / 255, 71 / 255, 1),
    'turquoise': (64 / 255, 224 / 255, 208 / 255, 1),
    'violet': (238 / 255, 130 / 255, 238 / 255, 1),
    'wheat': (245 / 255, 222 / 255, 179 / 255, 1),
    'white': (255 / 255, 255 / 255, 255 / 255, 1),
    'whitesmoke': (245 / 255, 245 / 255, 245 / 255, 1),
    'yellow': (255 / 255, 255 / 255, 0 / 255, 1),
    'yellowgreen': (154 / 255, 205 / 255, 50 / 255, 1),

    'activeborder': (0, 0, 1, 1),
    'activecaption': (0, 0, 1, 1),
    'appworkspace': (1, 1, 1, 1),
    'background': (1, 1, 1, 1),
    'buttonface': (0, 0, 0, 1),
    'buttonhighlight': (0.8, 0.8, 0.8, 1),
    'buttonshadow': (0.2, 0.2, 0.2, 1),
    'buttontext': (0, 0, 0, 1),
    'captiontext': (0, 0, 0, 1),
    'graytext': (0.2, 0.2, 0.2, 1),
    'highlight': (0, 0, 1, 1),
    'highlighttext': (0.8, 0.8, 0.8, 1),
    'inactiveborder': (0.2, 0.2, 0.2, 1),
    'inactivecaption': (0.8, 0.8, 0.8, 1),
    'inactivecaptiontext': (0.2, 0.2, 0.2, 1),
    'infobackground': (0.8, 0.8, 0.8, 1),
    'infotext': (0, 0, 0, 1),
    'menu': (0.8, 0.8, 0.8, 1),
    'menutext': (0.2, 0.2, 0.2, 1),
    'scrollbar': (0.8, 0.8, 0.8, 1),
    'threeddarkshadow': (0.2, 0.2, 0.2, 1),
    'threedface': (0.8, 0.8, 0.8, 1),
    'threedhighlight': (1, 1, 1, 1),
    'threedlightshadow': (0.2, 0.2, 0.2, 1),
    'threedshadow': (0.2, 0.2, 0.2, 1),
    'window': (0.8, 0.8, 0.8, 1),
    'windowframe': (0.8, 0.8, 0.8, 1),
    'windowtext': (0, 0, 0, 1),

    'none': (0, 0, 0, 0),
    'transparent': (0, 0, 0, 0),
}


RGBA = re.compile(r'rgba\((.+?)\)')
RGB = re.compile(r'rgb\((.+?)\)')
HEX_RRGGBB = re.compile('#[0-9a-f]{6}')
HEX_RGB = re.compile('#[0-9a-f]{3}')


def color(string, opacity=1):
    """Replace ``string`` representing a color by a RGBA tuple.
    See http://www.w3.org/TR/SVG/types.html#DataTypeColor
    """
    if not string:
        return (0, 0, 0, 0)

    string = string.strip().lower()

    if string in COLORS:
        r, g, b, a = COLORS[string]
        return (r, g, b, a * opacity)

    match = RGBA.search(string)
    if match:
        r, g, b, a = tuple(
            float(i.strip(' %')) / 100 if '%' in i else float(i) / 255
            for i in match.group(1).strip().split(','))
        return (r, g, b, a * 255 * opacity)

    match = RGB.search(string)
    if match:
        r, g, b = tuple(
            float(i.strip(' %')) / 100 if '%' in i else float(i) / 255
            for i in match.group(1).strip().split(','))
        return (r, g, b, opacity)

    match = HEX_RRGGBB.search(string)
    if match:
        plain_color = tuple(
            int(value, 16) / 255 for value in (
                string[1:3], string[3:5], string[5:7]))
        return plain_color + (opacity,)

    match = HEX_RGB.search(string)
    if match:
        plain_color = tuple(
            int(value, 16) / 15 for value in (
                string[1], string[2], string[3]))
        return plain_color + (opacity,)

    return (0, 0, 0, 1)


def normalize(string):
    """Normalize a string corresponding to an array of various values."""
    string = string.replace('E', 'e')
    string = re.sub('(?<!e)-', ' -', string)
    string = re.sub('[ \n\r\t,]+', ' ', string)
    string = re.sub(r'(\.[0-9-]+)(?=\.)', r'\1 ', string)
    return string.strip()


def fill_stroke(svg, node, font_size):
    fill = node.get('fill', 'black')
    fill_rule = node.get('fill-rule')

    if fill == 'none':
        fill = None
    if fill and fill != 'none':
        fill_color = color(fill)[0:-1]
        svg.stream.set_color_rgb(*fill_color)

    stroke = node.get('stroke')
    stroke_width = node.get('stroke-width', '1px')
    dash_array = normalize(node.get('stroke-dasharray', '')).split()
    offset = size(node.get('stroke-dashoffset', 0))
    if stroke:
        stroke_color = color(stroke)[0:-1]
        svg.stream.set_color_rgb(*stroke_color, stroke=True)
    if stroke_width:
        line_width = size(stroke_width, font_size)
        if line_width > 0:
            svg.stream.set_line_width(line_width)
    if dash_array:
        if not all(float(value) == 0 for value in dash_array) and not any(float(value) < 0 for value in dash_array):
            if offset < 0:
                sum_dashes = sum(float(value) for value in dash_array)
                offset = sum_dashes - abs(offset) % sum_dashes
            svg.stream.set_dash(dash_array, offset)

    if fill and stroke:
        svg.stream.fill_and_stroke(
            even_odd=True if fill_rule == 'evenodd' else False)
    elif stroke:
        svg.stream.stroke()
    elif fill:
        svg.stream.fill(even_odd=True if fill_rule == 'evenodd' else False)


def svg(svg, node, font_size):
    viewbox = svg.get_viewbox()
    scale_x = size(node.get('width'), font_size) / viewbox[2]
    scale_y = size(node.get('height'), font_size) / viewbox[3]
    svg.stream.transform(scale_x, 0, 0, scale_y, 0, 0)


def rect(svg, node, font_size):
    width = size(node.get('width', 0), font_size, svg.concrete_width)
    height = size(node.get('height', 0), font_size, svg.concrete_height)

    if width <= 0 or height <= 0:
        return

    svg.stream.rectangle(0, 0, width, height)
    fill_stroke(svg, node, font_size)


def circle(stream, node):
    pass


TAGS = {
#    'a': text,
    'circle': circle,
#    'clipPath': clip_path,
#    'ellipse': ellipse,
#    'filter': filter_,
#    'image': image,
#    'line': line,
#    'linearGradient': linear_gradient,
#    'marker': marker,
#    'mask': mask,
#    'path': path,
#    'pattern': pattern,
#    'polyline': polyline,
#    'polygon': polygon,
#    'radialGradient': radial_gradient,
    'rect': rect,
    'svg': svg,
#    'text': text,
#    'textPath': text,
#    'tspan': text,
#    'use': use,
}


def normalize(string):
    """Normalize a string corresponding to an array of various values."""
    string = string.replace('E', 'e')
    string = re.sub('(?<!e)-', ' -', string)
    string = re.sub('[ \n\r\t,]+', ' ', string)
    string = re.sub(r'(\.[0-9-]+)(?=\.)', r'\1 ', string)
    return string.strip()


def size(string, font_size=None, percentage_reference=None):
    if not string:
        return 0

    try:
        return float(string)
    except ValueError:
        # Not a float, try something else
        pass

    string = normalize(string).split(' ', 1)[0]
    if string.endswith('%'):
        assert percentage_reference is not None
        return float(string[:-1]) * percentage_reference / 100
    elif string.endswith('em'):
        assert font_size is not None
        return font_size * float(string[:-2])
    elif string.endswith('ex'):
        # Assume that 1em == 2ex
        assert font_size is not None
        return font_size * float(string[:-2]) / 2

    for unit, coefficient in UNITS.items():
        if string.endswith(unit):
            number = float(string[:-len(unit)])
            return number * (96 * coefficient if coefficient else 1)

    # Unknown size
    return 0


class SVG:
    def __init__(self, bytestring_svg):
        self.svg_tree = ElementTree.fromstring(bytestring_svg)

    def get_intrinsic_size(self, font_size):
        intrinsic_width = self.svg_tree.get('width', '100%')
        intrinsic_height = self.svg_tree.get('height', '100%')

        if '%' in intrinsic_width:
            intrinsic_width = None
        else:
            intrinsic_width = size(intrinsic_width, font_size)
        if '%' in intrinsic_height:
            intrinsic_height = None
        else:
            intrinsic_height = size(intrinsic_height, font_size)

        return intrinsic_width, intrinsic_height

    def get_viewbox(self):
        viewbox = self.svg_tree.get('viewBox')
        if viewbox:
            return tuple(float(number) for number in viewbox.split())

    def draw(self, stream, concrete_width, concrete_height, base_url,
             url_fetcher):
        self.stream = stream
        self.concrete_width = concrete_width
        self.concrete_height = concrete_height
        self.base_url = base_url
        self.url_fetcher = url_fetcher

        self.draw_node(self.svg_tree, size('12pt'))

    def draw_node(self, node, font_size):
        font_size = size(node.get('font-size', '1em'), font_size, font_size)

        self.stream.push_state()

        x = size(node.get('x', 0), font_size, self.concrete_width)
        y = size(node.get('y', 0), font_size, self.concrete_height)
        self.stream.transform(1, 0, 0, 1, x, y)

        local_name = node.tag.split('}', 1)[1]

        if local_name in TAGS:
            TAGS[local_name](self, node, font_size)

        for child in node:
            self.draw_node(child, font_size)

        self.stream.pop_state()