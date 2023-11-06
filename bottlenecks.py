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
            depth_map[tile] = 0
            get_depth_of_tile(agent, depth_map, tile, last_found_depth)
            last_found_depth = depth_map[tile]
    return depth_map

def get_depth_of_tile(agent: BasicAgent, depth_map: dict, tile: Point2DI, last_found_depth: int) -> None:
    """ Finds the distance between a walkable tile and its closest wall tile """
    current_depth = last_found_depth - 1
    while depth_map[tile] == 0:
        for offset_x in [-current_depth, 0, current_depth]:
            for offset_y in [-current_depth, 0, current_depth]:
                offset_coord = Point2DI(offset_x, offset_y)
                if agent.map_tools.is_valid_tile(offset_coord):
                    offset_2d = Point2D(offset_coord.x, offset_coord.y)
                    tile_2d = Point2D(tile.x, tile.y) + offset_2d
                    new_tile = Point2DI(tile_2d.x, tile_2d.y)
                    if not agent.map_tools.is_walkable(new_tile):
                        depth_map[tile] = current_depth
                        break
        current_depth = current_depth + 1
