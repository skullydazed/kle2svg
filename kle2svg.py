"""Converts a KLE layout into an SVG file.
"""
from decimal import Decimal

from colour import Color
from kle2xy import KLE2xy
from svgwrite import Drawing
from xml.dom import minidom

try:
    # Python 3+
    from html.parser import HTMLParser
except ImportError:
    # Python 2.6-2.7
    from HTMLParser import HTMLParser


unescape = HTMLParser().unescape


class KLE2SVG(object):
    def __init__(self, layout):
        self.key_corner_radius = 2
        self.plate_corner_radius = 5
        self.layout = KLE2xy(layout, invert_y=False)
        self.drawing = None
        self.plate = None
        self.stroke = 'black'
        self.fill = 'none'
        self.fill_opacity = 0
        self.keycap_margin = 2  # How much margin to leave around keys
        self.label_locations = ll = [
            # The first two columns are offsets from the top-left of the key,
            # measured in percentage of the key width.
            # The third column is the horizontal alignment
            # The fourth column is the vertical alignment
            (self.left_edge_label, self.top_edge_label, 'start', 'before-edge'),  # 0: top left
            (self.center_label, self.top_edge_label, 'middle', 'before-edge'),  # 1: top center
            (self.right_edge_label, self.top_edge_label, 'end', 'before-edge'),    # 2: top right
            (self.left_edge_label, self.center_label, 'start', 'middle'),        # 3: center left
            (self.center_label, self.center_label, 'middle', 'middle'),        # 4: center center
            (self.right_edge_label, self.center_label, 'end', 'middle'),          # 5: center right
            (self.left_edge_label, self.bottom_edge_label, 'start', 'after-edge'),   # 6: bottom left
            (self.center_label, self.bottom_edge_label, 'middle', 'after-edge'),   # 7: bottom center
            (self.right_edge_label, self.bottom_edge_label, 'end', 'after-edge'),     # 8: bottom right
            (self.left_edge_label, self.front_edge_label, 'start', 'middle'),         # 9: front left
            (self.center_label, self.front_edge_label, 'middle', 'middle'),         # 10: front center
            (self.right_edge_label, self.front_edge_label, 'end', 'middle'),           # 11: front right
        ]
        self.label_styles = [
            (ll[0], ll[6], ll[2], ll[8], ll[9], ll[11], ll[3], ll[5], ll[1], ll[4], ll[7], ll[10]),  # a:0
            (ll[1], ll[7], None, None, ll[9], ll[11], ll[4], None, None, None, None, ll[10]),        # a:1
            (ll[3], None, ll[5], None, ll[9], ll[11], None, None, ll[4], None, None, ll[10]),        # a:2
            (ll[4], None, None, None, ll[9], ll[11], None, None, None, None, None, ll[10]),          # a:3
            (ll[0], ll[6], ll[2], ll[8], ll[10], None, ll[3], ll[5], ll[1], ll[4], ll[7], None),     # a:4
            (ll[1], ll[7], None, None, ll[10], None, ll[4], None, None, None, None, None),           # a:5
            (ll[3], None, ll[5], None, ll[10], None, None, None, ll[4], None, None, None),           # a:6
            (ll[4], None, None, None, ll[10], None, None, None, None, None, None, None)              # a:7
        ]

    def left_edge_label(self, coord, length=None):
        """Returns the coordinate for a label just off the left edge

        :coord:
            The X or Y coordinate for the top-left corner of the key.

        :length:
            Not used. Included for compatibility purposes.
        """
        return coord + (self.layout.key_width * Decimal('0.08'))

    def top_edge_label(self, coord, length=None):
        """Returns the coordinate for a label just off the left or top edge

        :coord:
            The X or Y coordinate for the top-left corner of the key.

        :length:
            Not used. Included for compatibility purposes.
        """
        return coord + (self.layout.key_width * Decimal('0.2'))

    def right_edge_label(self, coord, length):
        """Returns the X coordinate for a label just off the right edge.

        :coord:
            The X coordinate for the left edge of the key.

        :length:
            The width or height of the key.
        """
        return coord + length - (self.layout.key_width * Decimal('0.08'))

    def bottom_edge_label(self, coord, length):
        """Returns the X coordinate for a label just off the bottom edge.

        :coord:
            The X coordinate for the left edge of the key.

        :length:
            The width or height of the key.
        """
        return coord + length - (self.layout.key_width * Decimal('0.125'))

    def center_label(self, coord, length):
        """Returns the coordinate for a label at the center of length.

        :coord:
            The coordinate for the top or left edge of the key.

        :length:
            The width or height or the key.
        """
        return coord + (length * Decimal('0.5'))

    def front_edge_label(self, coord, length):
        """Returns the coordinate for a label at the front of the key.

        :coord:
            The coordinate for the top or left edge of the key.

        :length:
            The width or height or the key.
        """
        return coord + self.layout.key_width

    def create(self):
        """Create the vector.
        """
        view_width = self.layout.width + 10
        view_height = self.layout.height + 10
        view_size = ('%smm' % view_width, '%smm' % view_height)
        plate_size = (float(self.layout.width), float(self.layout.height))

        self.drawing = Drawing(size=view_size, viewBox='-10 -10 %s %s' % (view_width, view_height))
        self.drawing.add(self.drawing.rect((-float(self.layout.key_width/4),-float(self.layout.key_width/4)), plate_size, rx=self.plate_corner_radius, ry=self.plate_corner_radius, fill=self.fill, fill_opacity=self.fill_opacity, stroke=self.stroke))

        for row in self.layout:
            for key in row:
                key_width = key['width'] * self.layout.key_width
                key_height = key['height'] * self.layout.key_width
                key_coords = (float(key['x'] - key_width/2), float(key['y'] - key_height/2))
                inner_key_coords = (float(key['x'] - key_width/2 + Decimal(self.keycap_margin)/4), float(key['y'] - key_height/2 + Decimal(self.keycap_margin)/4))
                inner_rect_size = (float(key_width - self.keycap_margin), float(key_height - self.keycap_margin))
                outer_rect_size = (float(key_width - Decimal(self.keycap_margin)/2), float(key_height - Decimal(self.keycap_margin/2)))
                inner_rect_color = Color(key['keycap_color'])
                outer_rect_color = Color(key['keycap_color'])
                outer_rect_color.luminance *= 0.8

                keygroup = self.drawing.add(self.drawing.g())
                if not key['decal']:
                    keygroup.add(self.drawing.rect(key_coords, outer_rect_size, rx=self.key_corner_radius, ry=self.key_corner_radius, stroke=key['border_color'], fill=outer_rect_color.hex))
                    keygroup.add(self.drawing.rect(inner_key_coords, inner_rect_size, rx=self.key_corner_radius, ry=self.key_corner_radius, stroke=key['border_color'], fill=inner_rect_color.hex))
                for i, label in enumerate(key['name'].split('\n')):
                    label = unescape(label)
                    label_style = self.label_styles[key['label_style']][i]
                    if label_style:
                        # Find label position relative to top-left corner
                        coords = (
                            label_style[0](Decimal(str(key_coords[0])), key_width),
                            label_style[1](Decimal(str(key_coords[1])), key_height)
                        )
                        keygroup.add(self.drawing.text(label, coords, fill=key['label_color'], stroke='none', font_size='%spt' % key['label_size'], text_anchor=label_style[2], alignment_baseline=label_style[3]))

        return self.drawing


if __name__ == '__main__':
    #svg = KLE2SVG('["",""],[""]')
    #svg = KLE2SVG(open('case_numpad_mx.kle').read())
    #svg = KLE2SVG(open('nantucket.kle').read())
    #svg = KLE2SVG(open('two.kle').read())
    svg = KLE2SVG(open('test.kle').read())
    file = svg.create()
    xml = minidom.parseString(file.tostring())
    print(xml.toprettyxml())
