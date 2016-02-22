
from mylib.hex import hex_256_encode
from mylib.math import clamp


class Color:
    
    def __init__(self, r, g, b):
        self.r = clamp(Math.round(r), 0, 255)
        self.g = clamp(Math.round(g), 0, 255)
        self.b = clamp(Math.round(b), 0, 255)

    def _interpolatedToward(self, c2, fraction):
        return Color(
                    self.r + (c2.r - self.r) * fraction,
                    self.g + (c2.g - self.g) * fraction,
                    self.b + (c2.b - self.b) * fraction)
    
    def _webString(self):
        return (
                    '#' +
                    hex_encode_256(self.r) +
                    hex_encode_256(self.g) +
                    hex_encode_256(self.b))


