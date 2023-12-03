from __future__ import annotations
from typing import TYPE_CHECKING, Union

from library import Point2D, Point2DI, BaseLocation
import json

from modules.extra import get_neighbours

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent


class Region:
    def __init__(self, agent, tiles: set[Point2DI], mid_point: Point2DI):
        self.agent = agent
        self.tiles = tiles
        self.mid_point = mid_point # not used currently
        self.tiles_as_tuples = set((pos.x, pos.y) for pos in tiles)
        

    def get_tiles(self):
        return self.tiles
    
    def get_tiles_as_tuples(self):
        return self.tiles_as_tuples

    def get_center(self):
        return self.mid_point

    def get_region_border(self) -> set[Point2DI]:
        border = set()
        for y in range(self.agent.map_tools.height):
            for x in range(self.agent.map_tools.width):
                tile = Point2DI(x, y)
                if tile not in self.tiles: # worked when tested in jupyter
                    for neighbour in get_neighbours(self.agent, tile):
                        if neighbour in self.tiles_as_tuples:
                            border.append(neighbour)

    @classmethod
    # parses a json file to set tile positions and mid point
    def parse_json(cls, json_obj: str):
        return cls(set(Point2DI(pos["x"], pos["y"]) for pos in json_obj["tiles"]), Point2DI(json_obj["center"]["x"], json_obj["center"]["y"]))
    

    
def get_region(agent: BasicAgent, regions: list[Region], tile_of_interest: Point2DI) -> Region:
    """Returns the region that the tile is in."""
    for tile in [tile_of_interest] + agent.map_tools.get_closest_tiles_to(tile): # idk if [tile_of_interest] is needed
        for region in regions:
            if tile in region[0]:
                return region

# def get region polygon (borders)
def get_region_polygon(agent: BasicAgent, regions: list[tuple[set[Point2DI], Point2DI]]) -> list[Point2DI]:
    """Returns the outer border tiles of the region"""
    pass

# calculate center of region (with Point2DI), using the already established calculate_center function
"""def calculate_center(region: set[Point2DI]) -> Point2DI:
    return Point2DI(*calculate_center(region_as_tuple(region)[0]))

def calculate_center(region: set[tuple[int, int]]) -> tuple[int, int]:
    return _calculate_center(region.as_tuple)"""

def calculate_center(region: Region) -> Point2D:
    x = sum(pos.x for pos in region.tiles)
    y = sum(pos.y for pos in region.tiles)
    return Point2D(x / len(region.tiles), y / len(region.tiles))

 
# get base locations in region
def get_base_locations_in_region(agent: BasicAgent, region) -> list[BaseLocation]:
    base_locations_in_region = []
    for base_location in agent.base_location_manager.base_locations:
        if base_location.position in region[0]:
            print("yes it is")
            base_locations_in_region.append(base_location)
    return base_locations_in_region

### ----------------- DEBUGGING ----------------- ###

def regions_debug(regions: list[tuple[set[Point2DI], Point2DI]]) -> dict[tuple[int, int], int]:
    return _regions_debug(regions, lambda pos: (pos.x, pos.y))

def regions_debug(regions: list[tuple[set[tuple[int, int]], tuple[int, int]]]) -> dict[tuple[int, int], int]:
    return _regions_debug(regions, lambda pos: (pos[0], pos[1]))

def _regions_debug(regions: list[tuple[set, tuple]], get_pos: callable) -> dict[tuple[int, int], int]:
    color = 1
    rmap = dict()
    for region in regions:
        for pos in region[0]:
            rmap[get_pos(pos)] = color
        print(f"region nr: {color}, center: {region[1]}")
        color += 1
    return rmap