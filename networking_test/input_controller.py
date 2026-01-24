import pygame


class InputController:
    def __init__(self, kb_poller):
        self.kb_poller = kb_poller

    def get_pressed_keys(self):
        return self.kb_poller.pressed


class PyGameInputController:
    def __init__(self):
        pass

    def get_pressed_keys(self):
        pressed_chars = set()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pressed_chars.add("q")

        keys = pygame.key.get_pressed()
        for i in range(len(keys)):
            if keys[i]:
                pressed_chars.add(chr(i))

        return pressed_chars


    def get_mouse_pressed(self):
        for event in pygame.event.get():
            pass

        mouse_clicked = pygame.mouse.get_pressed()[0]
        if mouse_clicked == True:
            mouse_pos = pygame.mouse.get_pos()
            return mouse_pos

        return None
