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

    map = get_list_of_bottlenecks(agent)
    list = set_gate_tiles(agent, map)
    return list


def get_gates(agent: BasicAgent) -> list:

    map = get_list_of_bottlenecks(agent)
    gates = set_gate_tiles(agent, map)
    gates = update_gate_clusters(agent, gates)
    #gates = build_gates(agent, gates)

    """complete_gates = []
    for gate_pair in gates:
        complete_gates.append(find_path(agent, gate_pair))"""
    return gates


def get_list_of_bottlenecks(agent: BasicAgent) -> dict:
    """ Returns a dict where each depth has associated tiles """
    tile_depths = init_map(agent)  # Insert every walkable tile with depth 0 in depth_map
    last_found_depth = 1    # The last found depth of a tile
    depth_map = {}  # Map of depths and their associated tiles

    for tile in tile_depths:
        depth = get_depth_of_tile(agent, tile, last_found_depth)
        if not depth in depth_map:    # Check if the depth has been found before
            depth_map[depth] = []
        depth_map[depth].append(tile)
        last_found_depth = depth   # Update last found depth 

    return depth_map

def get_depth_of_tile(agent: BasicAgent, tile: Point2DI, last_found_depth: int) -> None:
    """ Returns the distance between a walkable tile and its closest wall tile """
    current_depth = last_found_depth - 1
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
                    #depth_map[tile] = round(math.log2(current_depth) + 1)
                    depth = round(math.log2(current_depth) + 1)
                    break
                #wall_tiles_found += 1
        current_depth += 1

    return depth


def set_gate_tiles(agent: BasicAgent, depth_map: dict) -> list:
    """ Istället för att gå igenom random rutor så att det blir fel, kolla i labelled tiles för att sedan gå igenom
     deras neighbours så att vattnet alltid stiger utåt även för dem med samma djup
      Pseudokod:
         while curr_water_level >= 0:
         Är labelled tiles tom?
            for tile in labelled_tiles med djup curr_water_level + 1:
                hämta omärkta neighbours för tilen
                hämta alla tiles för curr_water_level
                har grannen curr_water_level som depth?
                    har grannen andra grannar med annan label?
                        Gör samma som innan dvs (sätt som gate)
                    sätt till samma label som den i labelled tiles
                labelled tiles bör vara uppdaterad så kolla nu om det finns fler tiles med curr_water_level fast som inte är granne till föregående djup
                Om det gör det så kolla i labelled tiles med samma djup och gör samma procedur. Om det sedan finns tiles kvar att märka på det djupet
                så står dem själva och bör bli labelled med ny label"""
    
    """ curr_water_level = len(depth_map)  
    labelled_tiles = {}     
    gate_clusters = []         
    current_label = 1
    region_pairs = []
    tiles = []
    while curr_water_level >= 0:
        for tile in depth_map.get(curr_water_level, []):
            neighbours = get_labelled_neighbours(agent, labelled_tiles, tile)
            if len(neighbours) > 0:
                values = list(neighbours.values())
                if len(set(values)) > 1: # Does the neighbours have different labels?
                    add_tile_to_gate_cluster(neighbours, tile, gate_clusters, region_pairs)
                    tiles.append(tile)
                labelled_tiles[tile] = values[0] # Give tile same label as any neighbour or the only neighbour
            else:
                # Give tiles without labelled neigbours a unique label
                labelled_tiles[tile] = current_label
                current_label += 1
            tiles_to_label
        curr_water_level -= 1

    return tiles #gate_clusters """

    """ Testa göra en is_neighbour funktion som kollar om en tile som är på rätt djup är granne till en redan labelled tile, sätt sedan dens label och ta väck den från listan
     while kommer då köra tills llistan är tom för varje djup """
    
    """ Annat alternativ är att skapa en most recently labelled tiles som uppdateras så om dem på djup 6 har blivit satta så är de uttyersta tilesen från dem most recently 
     sen när deras grannar på nästa djup är satta så tas dem från djup 6 väck och en "ring" av dem nyligen satta på djup 5 finns då, men labelled tiles finns kvar eftersom 
      man måste veta att de på djup 6 tex är lablled så att dem inte blir giltiga grannar senare. """

    curr_water_level = len(depth_map)  
    labelled_tiles = {}
    recently_labelled_tiles = {}
    gate_clusters = []         
    current_label = 1
    region_pairs = []

    depth_map_copy = depth_map.copy()
    test_list = []
   
    while curr_water_level >= 5:
        tiles_to_label = depth_map_copy.get(curr_water_level, [])
        print(len(tiles_to_label))
        curr = 0
        while tiles_to_label:
            #print(len(tiles_to_label))
            curr_tiles_to_label = get_curr_tiles_to_label(agent, recently_labelled_tiles, labelled_tiles, tiles_to_label)
            if curr == 0:
                print(len(curr_tiles_to_label))
            for tile in curr_tiles_to_label:
                neighbours = get_labelled_neighbours(agent, labelled_tiles, tile)
                if len(neighbours) > 0:
                    values = list(neighbours.values())
                    if len(set(values)) > 1: # Does the neighbours have different labels?
                        add_tile_to_gate_cluster(neighbours, tile, gate_clusters, region_pairs)
                        test_list.append(tile)
                    labelled_tiles[tile] = values[0] # Give tile same label as any neighbour or the only neighbour
                else:
                    # Give tiles without labelled neigbours a unique label
                    labelled_tiles[tile] = current_label
                    current_label += 1
                recently_labelled_tiles[tile] = labelled_tiles[tile]
                if tile in tiles_to_label:
                    tiles_to_label.remove(tile)
            curr += 1
            
        curr_water_level -= 1

    return test_list #gate_clusters


def get_curr_tiles_to_label(agent: BasicAgent, recently_labelled_tiles: dict, labelled_tiles: dict, tiles_to_label: list) -> list:

    if len(recently_labelled_tiles) == 0:
        return tiles_to_label
    
    curr_tiles_to_label = []
    tiles_to_remove = list(recently_labelled_tiles.keys())
    for tile in tiles_to_remove:
        neighbours = get_neighbours(agent, 1, tile)
        for neighbour in neighbours:
            if agent.map_tools.is_walkable(neighbour):
                if not neighbour in labelled_tiles:
                    if neighbour in tiles_to_label:
                        curr_tiles_to_label.append(neighbour)
        recently_labelled_tiles.pop(tile)
    
    return curr_tiles_to_label


def update_gate_clusters(agent: BasicAgent, gate_clusters: list) -> list:
    """ Removes all tiles not adjacent to wall """
    for gate_cluster in gate_clusters:
        gate_cluster_copy = gate_cluster.copy()
        for tile in gate_cluster_copy:
            neighbours = get_neighbours(agent, 1, tile)
            adj_to_wall = False
            for neighbour in neighbours:
                if not agent.map_tools.is_walkable(neighbour):
                    adj_to_wall = True
                    break
            if not adj_to_wall:
                gate_cluster.remove(tile)

    return gate_clusters

def build_gates(agent: BasicAgent, gate_clusters: list) -> list:
    """ Creates start and end tile for each bottleneck """

    # Select a tile from each gate_cluster
    selected_tiles = []
    for gate_cluster in gate_clusters:
        # If cluster not empty, chose first tile in cluster
        if gate_cluster:
            selected_tiles.append(gate_cluster.pop())

    # Build start and end tile for every gate 
    gate_positions = []    
    for i, start_tile in enumerate(selected_tiles):
        start_tile = Point2D(start_tile)
        shortest_dist = float('inf')
        closest_tile = None
        for j, end_tile in enumerate(selected_tiles):
            end_tile = Point2D(end_tile)
            if i != j:
                distance = agent.map_tools.get_ground_distance(start_tile, end_tile)
                if distance > 0 and (distance < shortest_dist):
                    shortest_dist = distance
                    closest_tile = end_tile

        gate_positions.append((Point2DI(start_tile), Point2DI(closest_tile)))
    
    return gate_positions


def find_path(agent: BasicAgent, gate_pair: tuple):
    """ Finds a walkable path from a start tile to an end tile """
    start = gate_pair[0]
    end = gate_pair[1]
    queue = deque([(start.x, start.y, [])])
    visited = set()

    while queue:
        x, y, path = queue.popleft()
        if (x, y) == (end.x, end.y):
            return [Point2DI(*pos) for pos in path + [(end.x, end.y)]]
        if (x, y) not in visited:
            visited.add((x, y))
        # Only want the vertical and horizontal neighbours, not diagonal
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        for nx, ny in neighbors:
                if agent.map_tools.is_valid_tile(nx, ny) and agent.map_tools.is_walkable(nx, ny):
                    queue.append((nx, ny, path + [(x, y)]))
    # No path found
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
    """ Returns a list of regions a tile is adjacent to """
    """adjacent_regions = []
    for neighbour in neighbours:
        curr_adj_region = neighbours[neighbour]
        if not curr_adj_region in adjacent_regions:
            adjacent_regions.append(curr_adj_region)

    return adjacent_regions"""
    adjacent_regions = set()
    for adj_region in neighbours.values():
        #curr_adj_region = neighbours[neighbour]
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


def get_neighbours(agent: BasicAgent, current_depth: int, tile: Point2DI) -> list:
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


def init_map(agent: BasicAgent) -> dict:
    """ Returns a depth map with every walkable tile in the game with depth 0 """
    depth_map = {}
    for y in range(agent.map_tools.height):
        for x in range(agent.map_tools.width):
            tile = Point2DI(x, y)
            if agent.map_tools.is_walkable(tile):
                depth_map[tile] = 0
    return depth_map
