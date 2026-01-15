from pynput import keyboard
# pip install pynput


class KBPoller:
    def __init__(self):
        self.pressed = set()
        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release,
            suppress=True
        )
        listener.start()

    def on_press(self, key):
        try:
            self.pressed.add(key.char.lower())
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            self.pressed.discard(key.char.lower())
        except AttributeError:
            pass
