import re
from xml.etree import ElementTree
from .colors import color


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
    line_cap = node.get('stroke-linecap', 'butt')
    line_join = node.get('stroke-linejoin', 'miter')
    miter_limit = float(node.get('stroke-miterlimit', 4))

    if stroke:
        stroke_color = color(stroke)[0:-1]
        svg.stream.set_color_rgb(*stroke_color, stroke=True)
    if stroke_width:
        line_width = size(stroke_width, font_size)
        if line_width > 0:
            svg.stream.set_line_width(line_width)
    if dash_array:
        if (not all(float(value) == 0 for value in dash_array) and
            not any(float(value) < 0 for value in dash_array)):
            if offset < 0:
                sum_dashes = sum(float(value) for value in dash_array)
                offset = sum_dashes - abs(offset) % sum_dashes
            svg.stream.set_dash(dash_array, offset)
    if line_cap in ('round', 'square'):
        line_cap = 1 if line_cap == 'round' else 2
    else:
        line_cap = 0
    if line_join in ('miter-clip', 'arc'):
        line_join = 'miter'
        raise NotImplementedError
    if line_join in ('round', 'bevel'):
        line_join = 1 if line_join == 'round' else 2
    if line_join == 'miter':
        line_join = 0
    svg.stream.set_line_cap(line_cap)
    svg.stream.set_line_join(line_join)
    svg.stream.set_miter_limit(miter_limit)


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