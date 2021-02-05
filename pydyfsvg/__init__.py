import re
from xml.etree import ElementTree


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


def size(string, font_size, viewport_width=None, viewport_height=None, reference='xy'):
    if not string:
        return 0

    try:
        return float(string)
    except ValueError:
        # Not a float, try something else
        pass

    string = normalize(string).split(' ', 1)[0]
    if string.endswith('%'):
        if reference == 'x':
            reference = viewport_width or 0
        elif reference == 'y':
            reference = viewport_height or 0
        elif reference == 'xy':
            reference = (
                (viewport_width ** 2 + viewport_height ** 2) ** .5 /
                2 ** .5)
        return float(string[:-1]) * reference / 100
    elif string.endswith('em'):
        return font_size * float(string[:-2])
    elif string.endswith('ex'):
        # Assume that 1em == 2ex
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

    def draw(self, context, concrete_width, concrete_height, base_url,
             url_fetcher):
        context.rectangle(0, 0, concrete_width, concrete_height)
        context.fill()
