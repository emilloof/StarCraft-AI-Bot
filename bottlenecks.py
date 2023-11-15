### Implementerad av: eriei013 (Byggnadsplacering)
### Beskrivning: Tar fram en lista av alla flaskhalsar där varje flaskhals innehåller flera flaskhalsrutor


from __future__ import annotations
from typing import TYPE_CHECKING
from library import Point2DI, Point2D

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent

from library import PLAYER_SELF, PLAYER_NEUTRAL

def get_bottle_map(agent: BasicAgent) -> dict:

    map = get_list_of_bottlenecks(agent)
    return map


def get_gates(agent: BasicAgent) -> list:

    map = get_list_of_bottlenecks(agent)
    gates = set_gate_tiles(agent, map)
    return gates


def get_list_of_bottlenecks(agent: BasicAgent) -> dict:
    """ Returns a dict where each tile is associated to a depth """
    
    depth_map = {}
    # Insert every walkable tile with depth 0 in map
    init_map(agent, depth_map)
    # The last found depth of a tile
    last_found_depth = 1
    found_depths = []
    divided_depth_map = {}

    for tile in depth_map:
        # Get the depth of the tile
        get_depth_of_tile(agent, depth_map, tile, last_found_depth)
        # Check if the list of that depth isnt initialized
        if not depth_map[tile] in divided_depth_map:
            divided_depth_map[depth_map[tile]] = []
        divided_depth_map[depth_map[tile]].append(tile)
        # Update last found depth 
        last_found_depth = depth_map[tile]

    return divided_depth_map

def get_depth_of_tile(agent: BasicAgent, depth_map: dict, tile: Point2DI, last_found_depth: int) -> None:
    """ Finds the distance between a walkable tile and its closest wall tile """
    current_depth = last_found_depth - 1
    while depth_map[tile] == 0:
        # neighbours with a current_depth as radius
        neighbours = get_neighbour_coords(agent, current_depth, tile)
        for neighbour in neighbours:
            # Is the tile a wall?
            if not agent.map_tools.is_walkable(neighbour):
                depth_map[tile] = current_depth
                break
        current_depth = current_depth + 1


def set_gate_tiles(agent: BasicAgent, divided_depth_map: dict) -> list:
    
    curr_water_level = len(divided_depth_map)  
    labelled_tiles = {}     # All labelled tiles
    gate_clusters = []         # All gate tiles
    current_label = 1
    used_labels = set()
    region_pairs = []
    
    while curr_water_level >= 11:
        for tile in divided_depth_map.get(curr_water_level, []):
            neighbours = get_labelled_neighbours(agent, labelled_tiles, tile)
            if len(neighbours) > 0:
                values = list(neighbours.values())
                # Does the neighbours have different labels?
                if len(set(values)) > 1:
                    add_tile_to_gate_cluster(neighbours, tile, gate_clusters, region_pairs)
                # Give tile same label as any neighbour or the only neighbour
                labelled_tiles[tile] = values[0]
            else:
                while current_label in used_labels:
                    current_label += 1
                labelled_tiles[tile] = current_label
                used_labels.add(current_label)
            print(neighbours)
        curr_water_level = curr_water_level - 1
    
    return gate_clusters

"""
def build_gate_list(agent: BasicAgent, gate_clusters: list) -> list:

    for gate_cluster in gate_clusters:
        for gate_tile in gate_cluster:
            neighbours = get_neighbour_coords(agent, 1, gate_tile)
            adj_to_wall = []
            for neighbour in neighbours:
                adj_to_wall.append(agent.map_tools.is_walkable(neighbour))
            if len(set(adj_to_wall)) > 1:
                gate_cluster.pop(gate_tile)
    
    return gate_clusters


def make_new_clusters(agent: BasicAgent, gate_clusters: list) -> list:

    new_clusters = []
    for gate_cluster in gate_clusters:
        for i in len(gate_cluster):
            if agent.map_tools.is_connected(gate_cluster[i], gate_cluster[i + 1]):
                pass
    return new_clusters
"""

def add_tile_to_gate_cluster(neighbours: dict, tile: Point2DI, gate_clusters: list, region_pairs: list) -> dict:
    """ Adds a tile to a specific cluster of gate tiles """
    adj_regions = get_adjacent_regions(neighbours)
    if adj_regions in region_pairs:
        curr = 0
        for region_pair in region_pairs:
            if adj_regions == region_pair:
                gate_clusters[curr].append(tile)
            curr = curr + 1
    else:
        region_pairs.append(adj_regions)
        gate_clusters.append([tile])


def get_adjacent_regions(neighbours: dict) -> list:
    """ Returns a list of regions a tile is adjecent to """
    adjacent_regions = []
    for neighbour in neighbours:
        curr_adj_region = neighbours[neighbour]
        if not curr_adj_region in adjacent_regions:
            adjacent_regions.append(curr_adj_region)

    return adjacent_regions


def get_labelled_neighbours(agent: BasicAgent, labelled_tiles: dict, tile: Point2DI) -> dict:
    """ Returns a dictionary of every labelled neighboring tile to a given tile """
    
    labelled_neighbours = {}
    # Only the closest neighbors (one square in radius)
    neighbours = get_neighbour_coords(agent, 1, tile)
    for neighbour in neighbours:
        if agent.map_tools.is_walkable(neighbour):
            # Is the neighbor labelled? If so, add neighbor to labelled neighbors
            if neighbour in labelled_tiles:
                labelled_neighbours[neighbour] = labelled_tiles[neighbour]

    return labelled_neighbours


def get_neighbour_coords(agent: BasicAgent, current_depth: int, tile: Point2DI) -> list:
    """ Returns a list of all in bound neighbours to a tile with a given radius """
    neighbour_coords = []
    offsets = get_offset_coords(current_depth)
    for offset in offsets:
        neighbour_2d = Point2D(tile.x, tile.y) + Point2D(*offset)
        neighbour_2di = Point2DI(neighbour_2d)
        if agent.map_tools.is_valid_tile(neighbour_2di):
            neighbour_coords.append(neighbour_2di)

    return neighbour_coords


def get_offset_coords(depth: int) -> list:
    """ Returns a list of all offset coordinates to a specific depth """
    offset_coordinates = []
    for x in range(-depth, depth + 1):
        for y in range(-depth, depth + 1):
            if x == depth or x == -depth or y == depth or y == -depth:
                offset_coordinates.append((x, y))

    return offset_coordinates


def init_map(agent: BasicAgent, map: dict) -> None:
    """ Returns a map with every walkable tile in the game map, with value 0 """
    for x in range(agent.map_tools.width):
        for y in range(agent.map_tools.height):
            tile = Point2DI(x, y)
            if agent.map_tools.is_walkable(tile):
                map[tile] = 0
    return map
