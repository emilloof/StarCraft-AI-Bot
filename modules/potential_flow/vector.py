import pygame
from functools import singledispatchmethod
from commandcenter import Point2D
from math import atan2, pi


class Vector(pygame.Vector2):

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], Point2D):
            args = args[0].x, args[0].y
        super().__init__(*args, **kwargs)

    @singledispatchmethod
    def cos(self, other) -> float:
        if not (self and other):
            return 0
        return self.dot(other) / (self.length() * other.length())

    @cos.register
    def _(self, other: Point2D) -> float:
        return self.cos(Vector(other))

    @singledispatchmethod
    def sin(self, other) -> float:
        if not (self and other):
            return 0
        return self.cross(other) / (self.length() * other.length())

    @sin.register
    def _(self, other: Point2D) -> float:
        return self.sin(Vector(other))

    """def angle_to(self, other: 'Vector') -> float:
        facing_vector = Vector(cos(self.unit.facing), sin(self.unit.facing))
        Calculate the angle between this vector and another vector
        # return atan2(sqrt(1 - self.cos(other)**2), self.cos(other))
        angle = atan2(self.sin(other), self.cos(other))
        return (angle + 2 * pi) % (2 * pi)    # [-pi, pi] -> [0, 2pi]"""

    def __add__(self, other):
        if isinstance(other, Point2D):
            return Point2D(self.x + other.x, self.y + other.y)
        return super().__add__(other)
