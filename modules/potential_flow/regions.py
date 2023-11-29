from __future__ import annotations
from typing import TYPE_CHECKING

from library import Point2DI, BaseLocation
import json

from modules.extra import get_neighbours

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent


class Region:
    def __init__(self, json_string: str):
        self.tiles, self.mid_point = self.parse_json(json_string)

    def get_tiles(self):
        return self.tiles

    def get_center(self):
        return self.mid_point

    @staticmethod
    # parses a json file to set tile positions and mid point
    def parse_json(json_string: str) -> (set[Point2DI], Point2DI):
        data = json.loads(json_string)
        tiles = set()
        for tiles in data["tiles"]:
            tiles.add(Point2DI(tiles["x"], tiles["y"]))
        center = data["center"]
        return tiles, center

def parse_regions(file_name: str) -> list[tuple[set[Point2DI], Point2DI]]:  # [(set[(83, 57), ...], (63, 92)), ...]
    with open(file_name) as json_file:
        data = json.load(json_file)
        return [
            (
                set(Point2DI(pos["x"], pos["y"]) for pos in region["tiles"]),
                Point2DI(region["center"]["x"], region["center"]["y"]),
            )
            for region in data
        ]

def regions_as_tuples(regions: list[tuple[set[Point2DI], Point2DI]]) -> list[tuple[set[tuple[int, int]], tuple[int, int]]]:
    return [region_as_tuple(region) for region in regions]

def region_as_tuple(region: tuple[set[Point2DI], Point2DI]) -> tuple[set[tuple[int, int]], tuple[int, int]]:
    return (
        set((pos.x, pos.y) for pos in region[0]),
        (region[1].x, region[1].y),
    )
    
def get_region(agent: BasicAgent, regions: list[tuple[set[Point2DI], Point2DI]], tile: Point2DI) -> tuple[set[Point2DI], Point2DI]:
    """Returns the region that the tile is in."""
    for neighbour_tile in agent.map_tools.get_closest_tiles_to(tile):
        for region in regions:
            if neighbour_tile in region[0]:
                return region

# def get region polygon (borders)
def get_region_polygon(agent: BasicAgent, regions: list[tuple[set[Point2DI], Point2DI]]) -> list[Point2DI]:
    """Returns the outer border tiles of the region"""
    pass

# calculate center of region (with Point2DI), using the already established calculate_center function
def calculate_center(region: set[Point2DI]) -> Point2DI:
    return Point2DI(*calculate_center(region_as_tuple(region)[0]))

# calculate center of region
def calculate_center(region: set[tuple]) -> tuple:
    x = 0
    y = 0
    for pos in region:
        x += pos[0]
        y += pos[1]
    return (x / len(region), y / len(region))


def get_region_border(agent: BasicAgent, region) -> list[Point2DI]:
    border = []
    for y in range(agent.map_tools.height):
        for x in range(agent.map_tools.width):
            if (x, y) not in region[0]:
                for neighbour in get_neighbours(agent, Point2DI(x, y)):
                    if neighbour in region[0]:
                        border.append(neighbour)

# get border perimeter

 
# get base locations in region
def get_base_locations_in_region(agent: BasicAgent, regions) -> list[BaseLocation]:
    base_locations_in_region = []
    for base_location in agent.base_location_manager.base_locations:
        for region in regions:
            if base_location.position in region[0]:
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