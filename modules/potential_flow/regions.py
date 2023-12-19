from __future__ import annotations
from typing import TYPE_CHECKING

from library import Point2D, Point2DI, BaseLocation
from functools import cached_property, cache
from modules.extra import get_adjacent_neighbours, parse_json_objects, get_closest, get_neighbours_within_distance

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent


class Region:

    def __init__(self, agent, tiles: set[Point2DI], mid_point: Point2DI):
        self.agent = agent
        self.tiles = tiles
        self.mid_point = mid_point    # not used currently
        self.mid_point_calculated = None
        self.tiles_as_tuples = {(pos.x, pos.y) for pos in tiles}
        # self.base_locations: list[BaseLocation] = []

    def on_start(self, id=None):
        _ = self.border
        _ = self.center
        _ = self.base_locations
        self.id = id

    @cached_property
    def border(self):
        border = set()
        for y in range(self.agent.map_tools.height):
            for x in range(self.agent.map_tools.width):
                tile = Point2DI(x, y)
                if tile not in self.tiles:
                    for neighbour in get_adjacent_neighbours(tile, self.agent):
                        if neighbour in self.tiles:
                            border.add(neighbour)

        # hard coded: removes two tiles that were "closing" region
        border -= {Point2DI(31, 119), Point2DI(120, 48)}
        #border -= {Point2DI(32, 119), Point2DI(31, 120), Point2DI(120, 47), Point2DI(119, 48)}
        #border -= {Point2DI(32, 121), Point2DI(33, 120), Point2DI(118, 47), Point2DI(119, 46)}
        #border -= {Point2DI(33, 122), Point2DI(34, 121), Point2DI(117, 46), Point2DI(118, 45)}
        return frozenset(border)

    @cached_property
    def center(self) -> Point2D:
        """Returns the center of the region"""
        if base_location := get_closest(self.base_locations, self.mid_point, lambda base_location: base_location.position):
            return base_location.position
        return self.mid_point
    

    @cached_property
    def base_locations(self) -> frozenset[BaseLocation]:
        return frozenset(base_location
                         for base_location in self.agent.base_location_manager.base_locations
                         if Point2DI(base_location.position) in self.tiles)

    @classmethod
    def parse_json(cls, agent: BasicAgent, json_obj: str):
        return cls(
            agent,
            {Point2DI(pos["x"], pos["y"])
             for pos in json_obj["tiles"]},
            Point2DI(json_obj["center"]["x"], json_obj["center"]["y"]),
        )


def calc_center(tiles: set[Point2DI]) -> Point2DI:
    """Returns the center of the region"""
    x = sum(pos.x for pos in tiles)
    y = sum(pos.y for pos in tiles)
    return Point2D(x / len(tiles), y / len(tiles))


class RegionManager:

    def __init__(self, agent: BasicAgent):
        self.agent = agent
        self.regions: set[Region] = {
            Region.parse_json(self.agent, data)
            for data in parse_json_objects("data/regions.json")
        }
        self.chokepoints: frozenset[Chokepoint] = frozenset(
            Chokepoint.parse_json(data) for data in parse_json_objects("data/chokepoints.json"))
        self.chokepoints_as_centers = frozenset(chokepoint.center
                                                for chokepoint in self.chokepoints)
        
    @cached_property
    def terrain_borders(self):
        border_tiles = set()
        for y in range(self.agent.map_tools.height):
            for x in range(self.agent.map_tools.width):
                tile = Point2DI(x, y)
                if self.agent.map_tools.is_walkable(tile):
                    for neighbour in get_adjacent_neighbours(tile, self.agent):
                        if not self.agent.map_tools.is_walkable(neighbour):
                            border_tiles.add(neighbour)
        return frozenset(border_tiles)
    
    def on_start(self):
        i = 1
        for region in self.regions:
            region.on_start(i)
            i += 1

        # init cached:
        self.regions_as_centers = frozenset(region.center for region in self.regions)
        _ = self.terrain_borders
        for y in range(self.agent.map_tools.height):
            for x in range(self.agent.map_tools.width):
                tile = Point2DI(x, y)
                if self.agent.map_tools.is_walkable(x, y) or tile in self.terrain_borders:
                    _ = self.get_region(tile)
        # _ = (self.get_region_by_center(region.center) for region in self.regions)

    # Unused
    @cache
    def get_region_by_center(self, pos: Point2D) -> Region:
        return next((region for region in self.regions if region.center == pos), None)

    @cache
    def get_exact_region(self, pos: Point2DI) -> Region | None:
        """Returns the region that the tile is in."""
        return next((region for region in self.regions if pos in region.tiles), None)

    @cache
    def get_region(self, tile_pos: Point2DI) -> Region:
        tile_pos = tile_pos.as_tile()
        if not (isinstance(tile_pos, Point2DI) and self.agent.map_tools.is_valid_tile(tile_pos) and (self.agent.map_tools.is_walkable(tile_pos.x, tile_pos.y) or tile_pos in self.terrain_borders)):
            raise TypeError(f"pos must be of type Point2DI, not {type(tile_pos)}")
        # sourcery skip: remove-unreachable-code
        """Returns the region that the tile is in or closest to."""
        if region := self.get_exact_region(tile_pos):
            return region
        # else
        tile_groups = get_neighbours_within_distance(tile_pos, distance=6, ordered=True)
        """for region in self.agent.region_manager.regions:
            if any(tile in region.tiles for tile in tiles):
                return region"""
        for group in tile_groups:
            for tile in group:
                if region := self.get_exact_region(tile):
                    return region
        raise ValueError(f"Could not find region for tile {tile_pos}")
        # return self.get_region_by_center(get_closest(self.regions_as_centers, pos))


class Chokepoint:

    def __init__(self, tiles: set[Point2DI], center: Point2DI):
        self.tiles: set[Point2DI] = tiles
        self.center_not_used: set[Point2DI] = center

    @cached_property
    def center(self):
        return calc_center(self.tiles)

    @classmethod
    def parse_json(cls, json_obj: str):
        return cls({Point2DI(int(pos["x"]), int(pos["y"]))
                    for pos in json_obj["tiles"]},
                   Point2DI(int(json_obj["center"]["x"]), int(json_obj["center"]["y"])))


# ----------------- DEBUGGING ----------------- #


def regions_debug(regions: list[tuple[set[Point2DI], Point2DI]]) -> dict[tuple[int, int], int]:
    return _regions_debug(regions, lambda pos: (pos.x, pos.y))


def regions_debug(regions: list[tuple[set[tuple[int, int]],
                  tuple[int, int]]]) -> dict[tuple[int, int], int]:
    return _regions_debug(regions, lambda pos: (pos[0], pos[1]))


def _regions_debug(regions: list[tuple[set, tuple]],
                   get_pos: callable) -> dict[tuple[int, int], int]:
    color = 1
    rmap = dict()
    for region in regions:
        for pos in region:
            rmap[get_pos(pos)] = color
        color += 1
    return rmap
