class Player:
    def __init__(self, id, x, y, speed_x=1, speed_y=1, size=10):
        self.id = id
        self.x = x
        self.y = y
        self.size = size
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.angle = 0

    def move(self, left, right, up, down, rotate, game_field):
        self.x += self.speed_x * right - self.speed_x * left
        self.y += self.speed_y * down - self.speed_y * up

        self.x, self.y, _, _ = game_field.clamp(self.x, self.y)

        if rotate:
            self.angle += 1

    def get_bounding_box(self):
        return (self.x - self.size // 2, self.y - self.size // 2, self.x + self.size // 2, self.y + self.size // 2)


class NPC:
    def __init__(self, x, y, speed_x=1, speed_y=1, size=20):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.size = size

    def move(self, game_field):
        self.x += self.speed_x
        self.y += self.speed_y

        self.x, self.y, x_edge, y_edge = game_field.clamp(self.x, self.y)

        if x_edge:
            self.speed_x = -self.speed_x

        if y_edge:
            self.speed_y = -self.speed_y

    def get_bounding_box(self):
        return (self.x - self.size // 2, self.y - self.size // 2, self.x + self.size // 2, self.y + self.size // 2)
