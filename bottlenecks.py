### Implementerad av: eriei013 (Byggnadsplacering)
### Beskrivning: Tar fram en lista av alla flaskhalsar där varje flaskhals innehåller flera flaskhalsrutor

from __future__ import annotations
from typing import TYPE_CHECKING
from library import Point2DI, Point2D
import math
from collections import deque

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent

from library import PLAYER_SELF, PLAYER_NEUTRAL

def get_bottle_map(agent: BasicAgent) -> dict:
    """ Used for debugging """
    map = get_list_of_bottlenecks(agent)
    return map


def get_gates(agent: BasicAgent) -> list:

    map = get_list_of_bottlenecks(agent)
    gates = set_gate_tiles(agent, map)
    gates = update_gate_clusters(agent, gates)
    gates = build_gates(agent, gates)

    complete_gates = []
    for gate_pair in gates:
        complete_gates.append(find_path(agent, gate_pair))
    return complete_gates


def get_list_of_bottlenecks(agent: BasicAgent) -> dict:
    """ Returns a dict where each depth has associated tiles """
    last_found_depth = 1   
    depth_map = {}  # Map of depths and their associated tiles

    for y in range(agent.map_tools.height):
        for x in range(agent.map_tools.width):
            tile = Point2DI(x, y)
            if agent.map_tools.is_walkable(tile):
                depth_map[tile] = 0
                depth = get_depth_of_tile(agent, tile, last_found_depth)
                if not depth in depth_map:    # Check if the depth has been found before
                    depth_map[depth] = []
                depth_map[depth].append(tile)
                last_found_depth = depth   # Update last found depth 

    return depth_map

def get_depth_of_tile(agent: BasicAgent, tile: Point2DI, last_found_depth: int) -> None:
    """ Returns the distance between a walkable tile and its closest wall tile """
    """current_depth = last_found_depth - 1
    depth = 0
    while depth == 0:
        neighbours = get_neighbours(agent, current_depth, tile)
        wall_tiles_found = 0
        wall_threshold = 0
        for neighbour in neighbours:
            if not agent.map_tools.is_walkable(neighbour):
                if wall_tiles_found == 0:
                    wall_threshold = ((12-current_depth)/28) + 1
                wall_tiles_found += 1
                if round(wall_threshold) <= wall_tiles_found:
                    depth = round(math.log2(current_depth) + 1)
                    break
        current_depth += 1

    return depth"""
    depth = 0
    current_depth = last_found_depth - 1
    while depth == 0:
        offsets = get_neighbours(agent, current_depth, tile)
        for offset in offsets:
            if agent.map_tools.is_valid_tile(offset):
                if not agent.map_tools.is_walkable(offset):
                    depth = current_depth
                    break
        current_depth = current_depth + 1
    return depth



def set_gate_tiles(agent: BasicAgent, depth_map: dict) -> list:
    
    """curr_water_level = len(depth_map) 
    labelled_tiles = {}     
    gate_clusters = []         
    current_label = 1
    region_pairs = []
    tiles = []
    while curr_water_level >= 11:
        listf = depth_map.get(curr_water_level, [])
        sorted_list = sorted(listf, key=lambda point: point.x)
        print("NEW DEPTH")
        for tile in sorted_list:
            print(tile)
            neighbours = get_labelled_neighbours(agent, labelled_tiles, tile)
            
            if len(neighbours) > 0:
                values = list(neighbours.values())
                if len(set(values)) > 1: # Does the neighbours have different labels?
                    add_tile_to_gate_cluster(neighbours, tile, gate_clusters, region_pairs)
                    print("TILEGATES", tile)
                    tiles.append(tile)
                labelled_tiles[tile] = values[0] # Give tile same label as any neighbour or the only neighbour
            else:
                # Give tiles without labelled neigbours a unique label
                labelled_tiles[tile] = current_label
                current_label += 1
        curr_water_level -= 1

    return tiles #gate_clusters """

    curr_water_level = len(depth_map)  
    labelled_tiles = {}
    recently_labelled_tiles = {}
    gate_clusters = []         
    current_label = 1
    region_pairs = []

    depth_map_copy = depth_map.copy()
    test_list = {}
    
    while curr_water_level >= 0:
        tiles_to_label = depth_map_copy.get(curr_water_level, [])   # Tiles at that level
        sorted_list = sorted(tiles_to_label, key=lambda point: (point.x, point.y))
        while sorted_list:
            curr_tiles_to_label = get_curr_tiles_to_label(agent, recently_labelled_tiles, labelled_tiles, sorted_list)
            if not curr_tiles_to_label:
                curr_tiles_to_label = sorted_list
            for tile in list(curr_tiles_to_label):
                neighbours = get_labelled_neighbours(agent, labelled_tiles, tile)
                if len(neighbours) > 0:
                    values = list(neighbours.values())
                    if len(set(values)) > 1: # Does the neighbours have different labels?
                        add_tile_to_gate_cluster(neighbours, tile, gate_clusters, region_pairs)
                    labelled_tiles[tile] = values[0] # Give tile same label as any neighbour or the only neighbour
                else:
                    # Give tiles without labelled neigbours a unique label
                    labelled_tiles[tile] = current_label
                    current_label += 1
                recently_labelled_tiles[tile] = labelled_tiles[tile]
                sorted_list.remove(tile)
            
        curr_water_level -= 1
    return gate_clusters


def get_curr_tiles_to_label(agent: BasicAgent, recently_labelled_tiles: dict, labelled_tiles: dict, tiles_to_label: list) -> list:
    # fixa så att man tar bort från recently efter hand
    if len(recently_labelled_tiles) == 0:
        return tiles_to_label
    
    curr_tiles_to_label = []
    tiles_to_remove = list(recently_labelled_tiles.keys())
    for tile in tiles_to_remove:
        neighbours = get_neighbours(agent, 1, tile)
        for neighbour in neighbours:
            if agent.map_tools.is_walkable(neighbour):
                if not neighbour in labelled_tiles:
                    if not neighbour in curr_tiles_to_label:
                        if neighbour in tiles_to_label:
                            curr_tiles_to_label.append(neighbour)
        #recently_labelled_tiles.pop(tile)
    
    return curr_tiles_to_label


def update_gate_clusters(agent: BasicAgent, gate_clusters: list) -> list:
    """ Removes all tiles not adjacent to wall """
    upd_gate_clusters = []

    for gate_cluster in gate_clusters:
        upd_cluster = {tile for tile in gate_cluster if tile_adj_to_wall(agent, tile)}
        if len(upd_cluster) >= 2:
            upd_gate_clusters.append(split_cluster(agent, upd_cluster))

    return upd_gate_clusters


def split_cluster(agent: BasicAgent, gate_cluster: set) -> list:
    """ Form groups of connected tiles from a gate cluster """
    visited = set()
    connected_components = []

    def dfs(point, component, gate_cluster):
        stack = [point]

        while stack:
            current_point = stack.pop()
            if current_point not in visited:
                visited.add(current_point)
                component.add(current_point)

                neighbors = [neighbor for neighbor in get_neighbours(agent, 1, current_point) 
                             if neighbor in gate_cluster and neighbor not in (visited, stack)]
                stack.extend(neighbors)

    for point in gate_cluster:
        if point not in visited:
            new_component = set()
            dfs(point, new_component, gate_cluster)
            connected_components.append(new_component)

    return connected_components


def build_gates(agent: BasicAgent, gate_clusters: list) -> list:
    """ Creates start and end tile for each bottleneck """
    selected_tiles = []
    for gate_cluster in gate_clusters:
        pair = []
        if len(gate_cluster) > 1:
            for x in gate_cluster:
                pair.append(x.pop())
            selected_tiles.append(pair)
    return selected_tiles


def find_path(agent: BasicAgent, gate_pair: list):
    """ Finds a walkable path from a start tile to an end tile """
    start = gate_pair[0]
    end = gate_pair[1]
    queue = [[start]]
    visited = []

    while queue:
        path = queue.pop(0)
        curr_tile = path[-1]
        if curr_tile not in visited:
            neighbours = get_neighbours(agent, 1, curr_tile)
            for neighbour in neighbours:
                if agent.map_tools.is_walkable(neighbour):
                    new_path = list(path)
                    new_path.append(neighbour)
                    queue.append(new_path)
                    if neighbour == end:
                        return new_path  
            visited.append(curr_tile)
    return None


def add_tile_to_gate_cluster(neighbours: dict, tile: Point2DI, gate_clusters: list, region_pairs: list) -> None:
    """ Adds a tile to a specific cluster of gate tiles """
    adj_regions = get_adjacent_regions(neighbours)
    if adj_regions in region_pairs:
        curr = 0
        for region_pair in region_pairs:
            if adj_regions == region_pair:
                gate_clusters[curr].add(tile)
            curr += 1
    else:
        region_pairs.append(adj_regions)
        gate_clusters.append({tile})


def get_adjacent_regions(neighbours: dict) -> list:
    """ Returns a set of regions a tile is adjacent to """
    adjacent_regions = set()
    for adj_region in neighbours.values():
        if not adj_region in adjacent_regions:
            adjacent_regions.add(adj_region)

    return adjacent_regions


def get_labelled_neighbours(agent: BasicAgent, labelled_tiles: dict, tile: Point2DI) -> dict:
    """ Returns a dictionary of every labelled neighboring tile to a given tile """
    neighbours = get_neighbours(agent, 1, tile) # Only the closest neighbors (one square in radius)
    labelled_neighbours = {}
    for neighbour in neighbours:
        if agent.map_tools.is_walkable(neighbour):
            if neighbour in labelled_tiles:      # Is the neighbor labelled? If so, add neighbor to labelled neighbors
                labelled_neighbours[neighbour] = labelled_tiles[neighbour]
    return labelled_neighbours


def tile_adj_to_wall(agent: BasicAgent, tile: Point2DI) -> bool:
    """ Returns true if a tile has a neighbouring wall tile, false otherwise """
    neighbours = get_neighbours(agent, 1, tile)
    adj_to_wall = False
    for neighbour in neighbours:
        if not agent.map_tools.is_walkable(neighbour):
            adj_to_wall = True
            break
    return adj_to_wall


def get_neighbours(agent: BasicAgent, current_depth: int, tile: Point2DI) -> list:
    """ Returns a list of all valid neighbours to a tile at a given radius """
    neighbour_coords = []
    offsets = get_offset_coords(current_depth)
    for offset in offsets:
        neighbour_2d = Point2D(tile.x, tile.y) + Point2D(*offset)
        neighbour_2di = Point2DI(neighbour_2d)
        if agent.map_tools.is_valid_tile(neighbour_2di):
            neighbour_coords.append(neighbour_2di)

    return neighbour_coords


def get_offset_coords(radius: int) -> list:
    """ Returns a list of all offset coordinates to a specific depth """
    offset_coordinates = []
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            if x == radius or x == -radius or y == radius or y == -radius:
                offset_coordinates.append((x, y))

    return offset_coordinates
