from __future__ import annotations
from typing import TYPE_CHECKING

from library import Point2D, Point2DI, BaseLocation

from modules.extra import get_neighbours, parse_json_objects, get_closest

if TYPE_CHECKING:
    from agents.improved_agent import ImprovedAgent
from functools import cached_property, cache


class Region:
    def __init__(self, agent, tiles: set[Point2DI], mid_point: Point2DI):
        self.agent = agent
        self.tiles = tiles
        self.mid_point = mid_point  # not used currently
        self.mid_point_calculated = None
        self.tiles_as_tuples = {(pos.x, pos.y) for pos in tiles}
        self.base_locations: list[BaseLocation] = []

        # init cached properties
        _ = self.border
        _ = self.center
        _ = self.base_locations

    def on_start(self):
        pass
        # self.base_locations = calc_base_locations(self.agent, self.tiles)
        # self.mid_point_calculated = calc_center(self.tiles)

    @cached_property
    def border(self):
        border = frozenset()
        for y in range(self.agent.map_tools.height):
            for x in range(self.agent.map_tools.width):
                tile = Point2DI(x, y)
                if tile not in self.tiles:
                    for neighbour in get_neighbours(tile, self.agent):
                        if neighbour in self.tiles:
                            border.add(neighbour)

        # hard coded: removes two tiles that were "closing" region
        border -= {Point2DI(31, 119), Point2DI(120, 48)}
        return border

    @cached_property
    def center(self) -> Point2D:
        """Returns the center of the region"""
        x = sum(pos.x for pos in self.tiles)
        y = sum(pos.y for pos in self.tiles)
        return Point2D(x / len(self.tiles), y / len(self.tiles))

    @cached_property
    def base_locations(self) -> frozenset[BaseLocation]:
        return frozenset(
            base_location
            for base_location in self.agent.base_location_manager.base_locations
            if Point2DI(base_location.position) in self.tiles
        )

    @classmethod
    def parse_json(cls, agent: ImprovedAgent, json_obj: str):
        return cls(
            agent,
            {Point2DI(pos["x"], pos["y"]) for pos in json_obj["tiles"]},
            Point2DI(json_obj["center"]["x"], json_obj["center"]["y"]),
        )


class RegionManager:
    def __init__(self, agent: ImprovedAgent):
        self.agent = agent
        self.regions: set[Region] = {Region.parse_json(self.agent, data)
                                     for data in parse_json_objects("data/regions.json")}
        self.regions_as_centers = frozenset(region.center for region in self.regions)

        self.chokepoints: frozenset[Chokepoint] = frozenset(Chokepoint.parse_json(
            data) for data in parse_json_objects("data/chokepoints.json"))
        self.chokepoints_as_centers = frozenset(
            chokepoint.center for chokepoint in self.chokepoints)

        # init cached:
        _ = (self.get_region_by_center(region.center) for region in self.regions)

    @cache
    def get_region_by_center(self, pos: Point2D) -> Region:
        return next((region for region in self.regions if region.center == pos), None)

    @cache
    def get_exact_region(self, pos: Point2DI) -> Region | None:
        """Returns the region that the tile is in."""
        return next((region for region in self.regions if pos in region.tiles), None)

    @cache
    def get_region(self, pos: Point2D | Point2DI) -> Region:
        # sourcery skip: remove-unreachable-code
        """Returns the region that the tile is in or closest to."""
        if region := self.get_exact_region(pos.as_tile()):
            return region
        # else
        return self.get_region_by_center(get_closest(self.regions_as_centers, pos))

        """tiles = [tile_of_interest] + get_neighbours(self.agent, tile_of_interest)
        for region in self.agent.regions:
            if any(tile in region.tiles for tile in tiles):
                return region"""


class Chokepoint:
    def __init__(self, tiles: set[Point2DI], center: Point2DI):
        self.tiles: set[Point2DI] = tiles
        self.center: set[Point2DI] = center

    @classmethod
    def parse_json(cls, json_obj: str):
        return cls({Point2DI(int(pos["x"]), int(pos["y"])) for pos in json_obj["tiles"]},
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
        for pos in region[0]:
            rmap[get_pos(pos)] = color
        print(f"region nr: {color}, center: {region[1]}")
        color += 1
    return rmap
