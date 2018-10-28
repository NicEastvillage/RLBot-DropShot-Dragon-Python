import math


def clamp(value, min, max):
    if value < min:
        return min
    if value > max:
        return max
    return value


def clamp11(value):
    return clamp(value, -1, 1)


def clamp01(value):
    return clamp(value, 0, 1)


def lerp(a, b, t):
    return (1 - t) * a + t * b


def sign(value):
    return 1 if value > 0 else -1


# A Hex coordinate. Works a lot like a vector, but the axis are q, r, and s with the constraint q + r + s = 0.
# See arena.hex_directions for more about the axis.
# Read more about axial coordinates here: https://www.redblobgames.com/grids/hexagons/
class Hex:
    def __init__(self, q=0, r=0):
        self.q = int(q)
        self.r = int(r)
        self.s = int(-q - r)

    def __add__(self, h):
        return Hex(self.q + h.q, self.r + h.r)

    def __sub__(self, h):
        return Hex(self.q - h.q, self.r - h.r)

    def length_manhattan(self):
        """ The manhattan distance to (0, 0), also known as taxi-cap distance. """
        return (abs(self.q) + abs(self.r) + abs(self.s)) / 2

    def distance_manhattan(self, h):
        """ The manhattan distance to another hex, also known as taxi-cap distance. """
        return (self - h).lengthManhattan()

    def is_zero(self):
        return self.q == 0 and self.r == 0 and self.s == 0

    def rotate60(self, direction):
        """ Rotates the Hex by 60 degrees the specified amount of times,
        where > 0 is counter-clockwise and < 0 is clockwise. """
        direction = direction % 6
        if direction < 0:
            direction += 6
        if direction == 0:
            return Hex(self.q, self.r)
        if direction == 1:
            return Hex(-self.r, -self.s)
        if direction == 2:
            return Hex(self.s, self.q)
        if direction == 3:
            return Hex(-self.q, -self.r)
        if direction == 4:
            return Hex(self.r, self.s)
        # dir == 5
        return Hex(-self.s, -self.q)

    def __str__(self):
        return "Hex(" + str(self.q) + ", " + str(self.r) + ", " + str(self.s) + ")"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.q == other.q and self.r == other.r
        return False

    def __ne__(self, other):
        return self.q != other.q and self.r != other.r

    def __hash__(self):
        return hash(str(self))


def hex_from_rounding(fq, fr):
    """ Construct a Hex from rounding two floating point q and r coordinates. """
    fs = -fq - fr

    rx = round(fq)
    ry = round(fr)
    rz = round(fs)

    x_diff = abs(rx - fq)
    y_diff = abs(ry - fr)
    z_diff = abs(rz - fs)

    # We reset the component with the largest change back to what the constraint rx + ry + rz = 0 requires
    if x_diff > y_diff and x_diff > z_diff:
        rx = -ry - rz
    elif y_diff > z_diff:
        ry = -rx - rz

    return Hex(rx, ry)
