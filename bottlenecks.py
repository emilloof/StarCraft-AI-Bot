from __future__ import annotations
from typing import TYPE_CHECKING
from library import Point2DI, Point2D

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent

from library import PLAYER_SELF, PLAYER_NEUTRAL

def get_list_of_bottlenecks(agent: BasicAgent) -> dict:
    """ Returns a list of bottlenecks in the game map """
    # Create map of each tile and associated depth
    depth_map = {}
    # The last found depth of a tile
    last_found_depth = 1
    for x in range(agent.map_tools.width):
        for y in range(agent.map_tools.height):
            tile = Point2DI(x, y)
            if agent.map_tools.is_walkable(tile):
                depth_map[tile] = 0
                get_depth_of_tile(agent, depth_map, tile, last_found_depth)
                last_found_depth = depth_map[tile]
            else:
                depth_map[tile] = 0
    return depth_map

def get_depth_of_tile(agent: BasicAgent, depth_map: dict, tile: Point2DI, last_found_depth: int) -> None:
    """ Finds the distance between a walkable tile and its closest wall tile """
    current_depth = 1
    while depth_map[tile] == 0:
        offsets = get_offset_coords(tile, current_depth)
        for offset in offsets:

            offset_2d = Point2D(offset[0], offset[1])
            tile_2d = Point2D(tile.x, tile.y) + offset_2d
            new_tile = Point2DI(tile_2d)
            if agent.map_tools.is_valid_tile(new_tile):
                if not agent.map_tools.is_walkable(new_tile):
                    depth_map[tile] = current_depth
                    break
        current_depth = current_depth + 1
    
def get_offset_coords(tile: Point2DI, depth: int) -> list:
    
    offset_coordinates = []

    for x in range(-depth, depth + 1):
        for y in range(-depth, depth + 1):
            # Calculate octile distance using max(dx, dy) and min(dx, dy)
            if x == depth or x == -depth:
                offset_coordinates.append((x, y))
            else:
                if y == depth or y == -depth:
                    offset_coordinates.append((x, y))

    return offset_coordinates

        

