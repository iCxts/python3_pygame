class Bullet:
    def __init__(self, x, y, speed_x, speed_y):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y

    def move(self, game_field):
        self.x += self.speed_x
        self.y += self.speed_y
