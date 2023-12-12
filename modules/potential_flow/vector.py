import pygame
from library import Point2D


class Vector(pygame.Vector2):
    def cos(self, other) -> float:
        if not (self and other):
            return 0
        return self.dot(other) / (self.length() * other.length())

    def sin(self, other) -> float:
        if not (self and other):
            return 0
        return self.cross(other) / (self.length() * other.length())

    def __add__(self, other):
        if isinstance(other, Point2D):
            return Point2D(self.x + other.x, self.y + other.y)
        return super().__add__(other)
