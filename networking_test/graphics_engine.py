import pygame


class GraphicsEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        pass

    def start_frame(self):
        pass

    def show_frame(self):
        pass

    def render_circle(self, x, y, radius, color):
        print(f"{color} circle is at:", x, y)

    def render_rectangle(self, x, y, width, height, color):
        print(f"{color} rectangle is at:", x, y)

    def render_line(self, x1, y1, x2, y2, color):
        print(f"{color} line is at:",  x1, y1, x2, y2)


class PyGameGraphicsEngine(GraphicsEngine):
    def __init__(self, width, height):
        super().__init__(width, height)
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))

    def start_frame(self):
        self.screen.fill("purple")

    def show_frame(self):
        pygame.display.flip()

    def render_circle(self, x, y, radius, color):
        pygame.draw.circle(self.screen, color, (x, y), radius)

    def render_rectangle(self, x, y, width, height, color):
        pygame.draw.rect(self.screen, color, (x, y, width, height))

    def render_line(self, x1, y1, x2, y2, color):
        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2))
