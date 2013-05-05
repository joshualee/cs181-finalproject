import random
import numpy
from numpy import matrix
from numpy import linalg
import game_interface

class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def scale_coordinate(self, scalar):
        x = self.x * scalar
        y = self.y * scalar

        return Coordinate(x, y)

    def __add__(self, other):
         x = self.x + other.x
         y = self.y + other.y
         coord = Coordinate(x,y)

         return coord

    def __sub__(self, other):
         x = self.x - other.x
         y = self.y - other.y
         coord = Coordinate(x,y)

         return coord

    def up(self):
        return Coordinate(self.x, self.y + 1)
    def left(self):
        return Coordinate(self.x - 1, self.y)
    def down(self):
        return Coordinate(self.x, self.y - 1)
    def right(self):
        return Coordinate(self.x + 1, self.y)

    @staticmethod
    def get_random_coordinate(max_x, max_y):
        x = random.randint(-max_x, max_x)
        y = random.randint(-max_y, max_y)

        return Coordinate(x, y)

    def to_list(self):
        return [[self.x], [self.y]]
