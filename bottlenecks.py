### Implementerad av: eriei013 (Byggnadsplacering)
### Beskrivning: Tar fram en lista innehållande listor som representerar flaskhalsar

from __future__ import annotations
from typing import TYPE_CHECKING
from library import Point2DI, Point2D
import math

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent

def get_bottlenecks(agent: BasicAgent, start_base_pos: Point2DI) -> list[list]:
    """ Beskrivning """
 
    gate_pairs = generate_bottleneck_bounds(agent)

    complete_bottlenecks = []
    for gate_pair in gate_pairs:
        if len(gate_pair) > 1:
            bottleneck = build_gate(agent, gate_pair) #
            if len(bottleneck) < 13: # Bottlenecks longer than 12 are too long
                complete_bottlenecks.append(bottleneck)

    return sort_bottlenecks(agent, complete_bottlenecks, start_base_pos)


def set_tile_depths(agent: BasicAgent) -> dict:
    """ Returns a dict where each depth has associated tiles """
    last_found_depth = 1   
    depths = {}  # Map of depths and their associated tiles

    for y in range(agent.map_tools.height):
        for x in range(agent.map_tools.width):
            tile = Point2DI(x, y)
            if agent.map_tools.is_walkable(tile):
                depths[tile] = 0
                depth = get_depth_of_tile(agent, tile, last_found_depth)
                if not depth in depths:    # Check if the depth has been found before
                    depths[depth] = []
                depths[depth].append(tile)
                last_found_depth = depth   # Update last found depth 

    return depths

def get_depth_of_tile(agent: BasicAgent, tile: Point2DI, last_found_depth: int) -> int:
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



def set_gate_clusters(agent: BasicAgent) -> list[set]:
    """ Beskrivning """

    depths = set_tile_depths(agent)
    curr_water_level = len(depths)  
    labelled_tiles = {}
    recently_labelled_tiles = {}
    gate_clusters = []         
    current_label = 1
    region_pairs = []
    depths_copy = depths.copy()
    
    while curr_water_level >= 0:
        tiles_to_label = depths_copy.get(curr_water_level, [])   # Tiles at that level
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
    return update_gate_clusters(agent, gate_clusters)


def get_curr_tiles_to_label(agent: BasicAgent, recently_labelled_tiles: dict, labelled_tiles: dict, tiles_to_label: list) -> list:
    """ Returns a list of tiles that should be labelled next at a certain depth """
    if not recently_labelled_tiles:
        return tiles_to_label
    
    curr_tiles_to_label = []
    tiles_to_remove = list(recently_labelled_tiles.keys())

    for tile in tiles_to_remove:
        neighbours = get_neighbours(agent, 1, tile)
        for neighbour in neighbours:
            if agent.map_tools.is_walkable(neighbour): 
                if neighbour not in labelled_tiles:
                    if neighbour not in curr_tiles_to_label:
                        if neighbour in tiles_to_label:
                            curr_tiles_to_label.append(neighbour)
    
    return curr_tiles_to_label


def update_gate_clusters(agent: BasicAgent, gate_clusters: list) -> list[set]:
    """ Removes all tiles not adjacent to wall """
    upd_gate_clusters = []

    for gate_cluster in gate_clusters:
        upd_cluster = {tile for tile in gate_cluster if tile_adj_to_wall(agent, tile)}
        if len(upd_cluster) >= 1:   # Removes empty sets
            upd_gate_clusters.append(split_cluster(agent, upd_cluster))

    return upd_gate_clusters


def split_cluster(agent: BasicAgent, gate_cluster: set) -> list[set]:
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


def generate_bottleneck_bounds(agent: BasicAgent) -> list[list]:
    """ Creates start and end tile for each bottleneck """
    
    selected_tiles = []
    tiles_to_pair = []
    gate_clusters = set_gate_clusters(agent)

    for gate_cluster in gate_clusters:
        pair = []
        if len(gate_cluster) > 1:
            for x in gate_cluster:
                pair.append(x.pop())
            selected_tiles.append(pair)
        else:
            tiles_to_pair.append(gate_cluster[0].pop())
    created_pairs = pair_tiles(tiles_to_pair)
    selected_tiles.extend(created_pairs)
    return selected_tiles


def pair_tiles(pairless_gate_tiles: list) -> list[list]:

    paired_tiles = []
    threshold = 17  # Magic number that can be changed after desire
    result = []

    for i in range(len(pairless_gate_tiles)):
        shortest_dist = float('inf')
        closest_tile = None
        start_tile = pairless_gate_tiles[i]

        if len(paired_tiles) == len(pairless_gate_tiles) - 1: # If odd number of tiles the last one does not get paired
            result.append([start_tile])

        for j in range(i + 1, len(pairless_gate_tiles)):
            end_tile = pairless_gate_tiles[j]
            if start_tile not in paired_tiles and end_tile not in paired_tiles:
                dist = distance_between_tiles(start_tile, end_tile)
                if dist < threshold:
                    if dist < shortest_dist:
                        shortest_dist = dist
                        closest_tile = end_tile
        if closest_tile:
            result.append([start_tile, closest_tile])
            paired_tiles.extend([start_tile, closest_tile])
        else:
            result.append([start_tile])

    return result


def build_gate(agent: BasicAgent, gate_pair: list) -> list:
    """ BFS algorithm that finds a walkable path from a start tile to an end tile """
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
                        return refine_bottleneck(agent, new_path)  
            visited.append(curr_tile)
    return None


def refine_bottleneck(agent: BasicAgent, bottleneck: list) -> list:
    """ Removes unnecessary tiles from a bottleneck """
    start_tile = None
    end_tile = None

    for index in range(len(bottleneck) // 2):
        curr_start = bottleneck[index]
        curr_end = bottleneck[-1 - index]

        if curr_start == curr_end:
            break
        if tile_adj_to_wall(agent, curr_start):
            start_tile = curr_start
        if tile_adj_to_wall(agent, curr_end):
            end_tile = curr_end
        
    refined_bottleneck = bottleneck[bottleneck.index(start_tile):bottleneck.index(end_tile) + 1]

    return refined_bottleneck


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


def distance_between_tiles(start: Point2DI, end: Point2DI) -> float:
    """ Calculates the euclidian distance between to tiles ignoring obstacles """
    return math.sqrt((start.x - end.x)**2 + (start.y - end.y)**2)


def get_adjacent_regions(neighbours: dict) -> set:
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
            if neighbour in labelled_tiles: # Is the neighbor labelled? If so, add neighbor to labelled neighbors
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


def get_offset_coords(radius: int) -> list[tuple]:
    """ Returns a list of all offset coordinates to a specific depth """
    offset_coordinates = []
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            if x == radius or x == -radius or y == radius or y == -radius:
                offset_coordinates.append((x, y))

    return offset_coordinates


def sort_bottlenecks(agent: BasicAgent, bottlenecks: list[list], start_base_pos: Point2DI) -> list[list]:
        """ Fetches bottlenecks and sorts them by closest to startbase position of agent """

        # Get one tile from each bottleneck
        selected_tiles = [bottleneck[0] for bottleneck in bottlenecks]
        
        # Get the distance to each bottleneck and its list index
        distances = [ 
            (distance_between_tiles(start_base_pos, tile), i)
            for i, tile in enumerate(selected_tiles) 
        ]
        # Sort the list by distance, where the closest one is first
        sorted_distances = sorted(distances, key=lambda x: x[0])

        # Add the bottleneck to nearest by its list index
        nearest_bottles = [bottlenecks[i] for _, i in sorted_distances]

        return nearest_bottles
