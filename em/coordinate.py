class coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def scale_coordinate(self, scalar):
        x = self.x * scalar
        y = self.y * scalar

        return coordinate(x, y)

    def __add__(self, other):
         x = self.x + other.x
         y = self.y + other.y
         coord = coordinate(x,y)

         return coord

    def __sub__(self, other):
         x = self.x - other.x
         y = self.y - other.y
         coord = coordinate(x,y)

         return coord

    def up(self):
        return coordinate(self.x, self.y + 1)
    def left(self):
        return coordinate(self.x - 1, self.y)
    def down(self):
        return coordinate(self.x, self.y - 1)
    def right(self):
        return coordinate(self.x + 1, self.y)

    def get_random_coordinate(max_x, max_y):
        x = random.randint(-max_x, max_x)
        y = random.randint(-max_y, max_y)

        return coordinate(x, y)

    def to_list(self):
        return [[self.x], [self.y]]
