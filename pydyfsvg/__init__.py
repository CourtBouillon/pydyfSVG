from xml.etree import ElementTree


class SVG:
    def __init__(self, bytestring_svg):
        self.svg_tree = ElementTree.fromstring(bytestring_svg)

    def get_size(self, font_size):
        intrinsic_width = intrinsic_height = 200
        return intrinsic_width, intrinsic_height

    def get_viewbox(self, font_size):
        viewbox = (0, 0, 80, 80)
        return viewbox

    def draw(self, context, concrete_width, concrete_height, base_url,
             url_fetcher):
        context.rectangle(0, 0, concrete_width, concrete_height)
        context.fill()
