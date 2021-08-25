import visualdebugger.visual_debugger
import numpy as np
import pygame


class HeatMapDebugger(visualdebugger.visual_debugger.VisualDebugger):
    def __init__(self):
        super(HeatMapDebugger, self).__init__()
        self.map_to_display = []
        self.color_map = {}
        self.squares = []

    def on_draw(self):
        self.screen.fill(self.background_color)
        for square in self.squares:
            pygame.draw.rect(self.screen, self.get_color_of_tile(square[1]), square[0])

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

        self.squares = []
        # create squares and bind them to a value
        for y_pos in range(len(self.map_to_display)):
            for x_pos in range(len(self.map_to_display[y_pos])):
                tile_val = self.map_to_display[y_pos][x_pos]

                tile_width = int((self.screen.get_width() - len(self.map_to_display[y_pos]) * self.tile_margin)
                                 / len(self.map_to_display[y_pos]))

                tile_height = int((self.screen.get_height() - len(self.map_to_display) * self.tile_margin)
                                  / len(self.map_to_display))

                rect_pos_x = x_pos * (tile_width + self.tile_margin) + self.tile_margin
                rect_pos_y = (len(self.map_to_display) - y_pos - 1) * \
                             (tile_height + self.tile_margin) + self.tile_margin

                self.squares.append((pygame.Rect(rect_pos_x, rect_pos_y, tile_width, tile_height),
                                     tile_val))

        self.on_draw()

    def set_display_values(self, map_values):
        """
        Set what map that should be displayed, it has to be a 2d list
        or a 2d numpy array. Where every row in the list has the same length
        :param map_values: [[], []. [], ...]
        :return:
        """
        try:
            assert isinstance(map_values, (list, np.ndarray)) and len(map_values)
            first_row = map_values[0]
            for row in map_values:
                assert isinstance(row, (list, np.ndarray)) and len(row)
                assert(len(first_row) == len(row))
                for number in row:
                    assert isinstance(number, (int, float))
            self.map_to_display = map_values

        except AssertionError:
            print("The map you set for debugger must be a list or numpy.array. It cant be empty and "
                  "every row has to have the same length and every element must be a int or float")

    def set_color_map(self, color_map):
        """
        Setter for the colormap. takes a dict with tuple of interval as key and rgb value it should represent as value.
        interval is (include, exclude).

        :param color_map: {interval(include, exclude): color (r, g, b)}.
                          {(start of interval included, end of interval excluded): (r, g, b)}
        :return: None, sets the colormap of the Heatmap
        """
        try:
            assert isinstance(color_map, dict) and len(color_map)
            occupied_intervals = []
            for key in color_map.keys():
                assert isinstance(key, tuple) and isinstance(color_map[key], tuple) and \
                       len(key) == 2 and len(color_map[key]) == 3

                assert key[0] <= key[1] and isinstance(key[0], (int, float)) \
                       and isinstance(key[1], (int, float))

                for interval in occupied_intervals:
                    if not (key[1] <= interval[0] or key[0] >= interval[1]):
                        print("interval: " + str(key) + " overlapped with: " + str(interval))
                        raise ValueError

                occupied_intervals.append(key)

                for color_val in color_map[key]:
                    assert 0 <= color_val <= 255

            self.color_map = color_map

        except AssertionError:
            print("The colormap provided was not correctly formatted")
        except ValueError:
            print("The colormap provided had overlapping intervals")

    def get_color_of_tile(self, tile_value):
        for interval in self.color_map.keys():
            if interval[0] <= tile_value < interval[1] or interval[0] == tile_value:
                return self.color_map[interval]
        return 0, 0, 0
