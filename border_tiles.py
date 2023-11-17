
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
    # Insert every walkable tile with depth 0 in map
    init_map(agent, depth_map)
    # The last found depth of a tile
    last_found_depth = 1
    for tile in depth_map:
        get_depth_of_tile(agent, depth_map, tile, last_found_depth)
        last_found_depth = depth_map[tile]
    return depth_map


def get_depth_of_tile(agent: BasicAgent, depth_map: dict, tile: Point2DI, last_found_depth: int) -> None:
    """ Finds the distance between a walkable tile and its closest wall tile """
    current_depth = last_found_depth - 1
    while depth_map[tile] == 0:
        offsets = get_offset_coords(current_depth)
        #if current_depth != 1:
        #    break
        for offset in offsets:
            offset_2d = Point2D(offset[0], offset[1])
            new_tile_2d = Point2D(tile.x, tile.y) + offset_2d
            new_tile_2di = Point2DI(new_tile_2d)
            if agent.map_tools.is_valid_tile(new_tile_2di):
                if not agent.map_tools.is_walkable(new_tile_2di):
                    depth_map[tile] = current_depth
                    break
        current_depth = current_depth + 1

def init_map(agent: BasicAgent, map: dict) -> None:
    """ Insert every walkable tile in game to map with value 0 """
    for x in range(agent.map_tools.width):
        for y in range(agent.map_tools.height):
            tile = Point2DI(x, y)
            if agent.map_tools.is_walkable(tile):
                """offset_cords = get_offset_coords(1)
                neighbour = False
                for cords in offset_cords:
                    neighbour = Point2D(tile) + Point2D(*cords)
                    if not agent.map_tools.is_walkable(neighbour):
                        neighbour = True
                        break
                if neighbour:
                    map[tile] = 0"""
                map[tile] = 0
    return map


def get_offset_coords(depth: int) -> list:
    """ Returns a list of all offset coordinates to a specific depth and tile """
    offset_coordinates = []
    for x in range(-depth, depth + 1):
        for y in range(-depth, depth + 1):
            if x == depth or x == -depth:
                offset_coordinates.append((x, y))
            else:
                if y == depth or y == -depth:
                    offset_coordinates.append((x, y))

    return offset_coordinates

# def get list of all border tiles in the map
def get_border_tiles(agent: BasicAgent) -> list[Point2DI]:
    """
    Gets a list of all border tiles on the map.
    """
    border_tiles: list[Point2DI] = []
    for x in range(agent.map_tools.width):
        for y in range(agent.map_tools.height):
            tile = Point2DI(x, y)
            if agent.map_tools.is_valid_tile(tile):
                if not agent.map_tools.is_walkable(tile):
                    border_tiles.append(tile)
    return border_tiles