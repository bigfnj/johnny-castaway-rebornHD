"""Hash-bound decoded masks avoid a Pillow dependency in the native container."""
import native_core as core


class LMask:
    mode = 'L'

    def __init__(self, canvas, data):
        self.width, self.height = canvas
        self.size = (self.width, self.height)
        core.require(len(data) == self.width * self.height, 'decoded mask dimensions')
        self.data = data

    def tobytes(self):
        return self.data
