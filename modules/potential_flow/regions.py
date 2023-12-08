from __future__ import annotations
from functools import cache
from typing import TYPE_CHECKING, Hashable, Iterable, Union

from library import Point2D, Point2DI, BaseLocation

from modules.extra import get_neighbours, get_neighbours2, tuple_fromto_tile

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent


class Region:
    def __init__(self, agent, tiles: set[Point2DI], mid_point: Point2DI):
        self.agent = agent
        self.tiles = tiles
        self.mid_point = mid_point  # not used currently
        self.mid_point_calculated = None
        self.tiles_as_tuples = {(pos.x, pos.y) for pos in tiles}
        self.border: set[Point2DI] = set()
        self.base_locations: list[BaseLocation] = []

    def on_start(self):
        self.border = fix_region_border(
            self.agent, calc_region_border(
                self.agent, self.tiles))  # **{"o": Point2DI}
        self.base_locations = calc_base_locations(self.agent, self.tiles)
        self.mid_point_calculated = calc_center(self.tiles)

    @property
    def center(self):
        return self.mid_point_calculated

    @classmethod
    def parse_json(cls, agent: BasicAgent, json_obj: str):
        return cls(
            agent,
            {Point2DI(pos["x"], pos["y"]) for pos in json_obj["tiles"]},
            Point2DI(json_obj["center"]["x"], json_obj["center"]["y"]),
        )


# @cache
def get_region(agent: BasicAgent, tile_of_interest: Point2DI) -> Region:
    """Returns the region that the tile is in."""
    tiles = [tile_of_interest] + get_neighbours(agent, tile_of_interest)
    for region in agent.regions:
        if any(tile in region.tiles for tile in tiles):
            return region


@cache
def get_region_old(agent: BasicAgent,
                   tile_s_of_interest: Union[Point2DI, Hashable[Iterable]]) -> Region:
    """Returns the region that the tile is in."""

    tiles = tile_s_of_interest if isinstance(tile_s_of_interest, Iterable) else [tile_s_of_interest]

    neighbours = get_neighbours(agent, tile_s_of_interest)
    tiles = [tile_s_of_interest] + neighbours
    for region in agent.regions:
        if any(tile in region.tiles for tile in tiles):
            return region

    # if not found any; do recursive call
    # return get_region(agent, frozenset(tile for curr_tile in tiles for tile
    # in get_neighbours(agent, curr_tile)))


def calc_base_locations(agent: BasicAgent, tiles: set[Point2DI]) -> list[BaseLocation]:
    return [
        base_location
        for base_location in agent.base_location_manager.base_locations
        if Point2DI(base_location.position) in tiles
    ]


def fix_region_border(agent: BasicAgent, border_tiles: set[Point2DI]) -> set[Point2DI]:
    """Returns the outer border tiles of the region"""
    tiles_to_remove = {(31, 119), (120, 48)}
    for tile in {Point2DI(tile[0], tile[1]) for tile in tiles_to_remove}:
        if tile in border_tiles:
            border_tiles.remove(tile)
    return border_tiles


def calc_region_border(agent: BasicAgent, tiles: set[Point2DI]) -> set[Point2DI]:
    """Calculates the outer border tiles of the region"""
    border = set()
    for y in range(agent.map_tools.height):
        for x in range(agent.map_tools.width):
            tile = Point2DI(x, y)
            if tile not in tiles:
                for neighbour in get_neighbours(agent, tile):
                    if neighbour in tiles:
                        border.add(neighbour)
    return border


@tuple_fromto_tile
def calc_region_border_old(agent, tiles: set[tuple]) -> set[Point2DI]:
    border = set()
    for y in range(agent.map_tools.height):
        for x in range(agent.map_tools.width):
            tile = (x, y)
            if tile not in tiles:  # worked when tested in jupyter
                for neighbour in get_neighbours2(agent, tile):
                    if neighbour in tiles:
                        border.add(neighbour)
    return border


def calc_center(tiles: set[Point2DI]) -> Point2D:
    """Calculates the center of the region"""
    x = sum(pos.x for pos in tiles)
    y = sum(pos.y for pos in tiles)
    return Point2D(x / len(tiles), y / len(tiles))

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
