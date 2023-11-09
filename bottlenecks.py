### Implementerad av: eriei013 (Byggnadsplacering)
### Beskrivning: Tar fram en lista av alla flaskhalsar där varje flaskhals innehåller flera flaskhalsrutor


from __future__ import annotations
from typing import TYPE_CHECKING
from library import Point2DI, Point2D

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent

from library import PLAYER_SELF, PLAYER_NEUTRAL

def get_bottlenecks(agent: BasicAgent) -> list:

    map = get_list_of_bottlenecks(agent)
    gates = set_gate_tiles(agent, map)
    return gates

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
        offsets = get_offset_coords(tile, current_depth)
        for offset in offsets:
            offset_2d = Point2D(offset[0], offset[1])
            new_tile_2d = Point2D(tile.x, tile.y) + offset_2d
            new_tile_2di = Point2DI(new_tile_2d)
            if agent.map_tools.is_valid_tile(new_tile_2di):
                if not agent.map_tools.is_walkable(new_tile_2di):
                    depth_map[tile] = current_depth
                    break
        current_depth = current_depth + 1
    
def get_offset_coords(tile: Point2DI, depth: int) -> list:
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


def set_gate_tiles(agent: BasicAgent, depth_map: dict) -> list:
    
    curr_water_level = 15   # 20 = maxdepth (Magic number, fix!!)
    labelled_tiles = {}     # All labelled tiles
    gate_tiles = []         # All gate tiles
    
    while curr_water_level >= 0:
        for tile in depth_map:
            if depth_map[tile] == curr_water_level:
                neighbours = get_labelled_neighbours(agent, labelled_tiles, tile)
                if len(neighbours) > 1:
                    values = []
                    for value in neighbours.values():
                        values.append(value)
                    x = all(values)
                    if not x:
                        gate_tiles.append(tile)
                    
                    labelled_tiles[tile] = list(neighbours.values())[0]

                elif len(neighbours) == 1:
                    labelled_tiles[tile] = list(neighbours.values())[0]
                else:
                    labelled_tiles[tile] = depth_map[tile]
        curr_water_level = curr_water_level - 1

    return gate_tiles
    

def get_labelled_neighbours(agent: BasicAgent, labelled_tiles: dict, tile: Point2DI) -> dict:
    
    labelled_neighbours = {}

    for labelled_tile in labelled_tiles:
        if agent.map_tools.is_connected(tile, labelled_tile):
            labelled_neighbours[labelled_tile] = labelled_tiles[labelled_tile]
        
    return labelled_neighbours


def init_map(agent: BasicAgent, map: dict) -> None:
    """ Insert every walkable tile in game to map with value 0 """
    for x in range(agent.map_tools.width):
        for y in range(agent.map_tools.height):
            tile = Point2DI(x, y)
            if agent.map_tools.is_walkable(tile):
                map[tile] = 0
    return map
