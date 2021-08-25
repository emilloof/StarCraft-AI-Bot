import visualdebugger.visual_debugger
import numpy as np
import pygame
import math


class FlowDebugger(visualdebugger.visual_debugger.VisualDebugger):
    def __init__(self):
        super(FlowDebugger, self).__init__()
        self.direction_map = []
        self.arrows = []
        self.arrow_color = (255, 0, 0)

    def on_draw(self):
        self.screen.fill(self.background_color)
        for arrow in self.arrows:
            self.screen.blit(pygame.transform.rotate(arrow[0], math.degrees(arrow[2])), arrow[1])

        pygame.display.flip()
        self.screen.fill(self.background_color)

    def on_step(self, fun=None):
        super().on_step(fun)

        if self.should_update:
            self.private_on_step()

    def private_on_step(self):
        if not self.screen:
            self.on_start()
        else:
            pygame.event.pump()

        self.arrows = []
        # create squares and bind them to a value
        for y_pos in range(len(self.direction_map)):
            for x_pos in range(len(self.direction_map[y_pos])):
                tile_width = int((self.screen.get_width() -
                                  len(self.direction_map[y_pos]) * self.tile_margin) / len(self.direction_map[y_pos]))
                tile_height = int((self.screen.get_height() -
                                   len(self.direction_map) * self.tile_margin) / len(self.direction_map))

                surface = pygame.Surface((tile_width, tile_height))

                pygame.draw.polygon(surface, self.arrow_color, ((0+tile_width/6, tile_height/3),
                                                                (0+tile_width/6, 2*tile_height/3),
                                                                (2*tile_width/4, 2*tile_height/3),
                                                                (2*tile_width/4, 5*tile_height/6),
                                                                (5*tile_width/6, tile_height/2),
                                                                (2*tile_width/4, 0+tile_height/6),
                                                                (2*tile_width/4, tile_height/3))
                                    )

                dest_x = x_pos * (tile_width + self.tile_margin) + self.tile_margin
                # y is flipped in order to match sc2 coords
                dest_y = (len(self.direction_map) - y_pos - 1) * (tile_height + self.tile_margin) + self.tile_margin
                position = (dest_x, dest_y)
                self.arrows.append((surface, position, self.direction_map[y_pos][x_pos]))
        self.on_draw()

    def set_display_values(self, map_values):
        """
        Set what map that should be displayed, it has to be a 2d list
        or a 2d numpy array. Where every row in the list has the same length.
        The values has to be ints or floats between 0 and 2*pi
        :param map_values: [[], []. [], ...]
        :return: none, sets the values to display
        """
        try:
            assert isinstance(map_values, (list, np.ndarray)) and len(map_values)
            first_row = map_values[0]
            for row in map_values:
                assert isinstance(row, (list, np.ndarray)) and len(row)
                assert(len(first_row) == len(row))
                for column in row:
                    assert isinstance(column, (int, float))
                    assert 0 <= column <= 2*math.pi

            self.direction_map = map_values

        except AssertionError:
            print("The map you set for debugger must be a list or numpy.array. It cant be empty and "
                  "every row has to have the same length")
