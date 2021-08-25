import time
import pygame


class VisualDebugger:
    def __init__(self):
        self.default_width = 152*5
        self.default_height = 176*5
        self.tile_margin = 1
        self.background_color = (0, 0, 0)
        self.screen = None
        self.update_frequency = 0.5  # update frequency in Hz (updates per second)
        self.last_update = 0
        self.should_update = True

    def on_start(self):
        self.screen = pygame.display.set_mode((self.default_width, self.default_height))

    def on_step(self, fun=None):
        if time.time() - self.last_update > 1/self.update_frequency:  # updates if enough time has passed
            if callable(fun):
                fun()

            self.last_update = time.time()
            self.should_update = True

        else:
            self.should_update = False

    def set_update_frequency(self, new_frequency):
        self.update_frequency = new_frequency

    def set_tile_margin(self, margin):
        self.tile_margin = margin
