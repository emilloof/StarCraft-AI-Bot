"""
Module with functions that support use of PyCommandCenter and BasicAgent:

Functions:
get_addon
find_producer
exists_producer_for
get_id
get_worker_type
has_prerequisites
unit_types_by_condition

Methods:
Point2D.square_distance - better way to calculate the shortest distance.
Point2D.__eq__ - overrides how to points are compared.
Point2DI.square_distance - better way to calculate the shortest distance.
Point2DI.__add__ - overrides how two points are added.
BaseLocation.__repr__ - overrides how a base location is represented.
Color.__floordiv__ - overrides floor division (divides RGB-color with int).
"""
from __future__ import annotations
from functools import cache
import json
from math import sqrt, atan2, pi
from typing import TYPE_CHECKING, Iterable, Optional, Union

if TYPE_CHECKING:
    from py_unit import PyUnit
    from agents.basic_agent import BasicAgent

import tasks
from functools import singledispatch
from library import UnitType, PLAYER_SELF, Point2D, UPGRADE_ID, Point2DI, UNIT_TYPEID, \
    Color, BaseLocation, Race, PLAYER_ENEMY


def parse_json_objects(file_name: str) -> list:
    with open(file_name) as json_file:
        return json.load(json_file)


def get_addon(agent: BasicAgent, candidate: PyUnit) -> Optional[PyUnit]:
    # sourcery skip: use-next
    """
    Looks through all units and looks if there is an addon connected to the supplied candidate.

    :return: Addon unit if the unit "candidate" has an addon.
    """
    for py_unit in agent.unit_collection.get_group(PLAYER_SELF):
        if py_unit.unit_type.is_addon and py_unit.is_alive and py_unit.is_completed \
                and py_unit.tile_position == candidate.tile_position + Point2DI(3, 0):
            return py_unit
    return None


def find_producer(agent: BasicAgent, unit_type: UnitType) -> Optional[PyUnit]:
    # sourcery skip: assign-if-exp, de-morgan, merge-isinstance
    """
    Goes through all units and tries to find a unit which can produce the given unit_type at this very moment. Ignores
    units which non-idle.

    :return: A unit which can build unit_type, None if there is no such unit.
    """
    data = agent.tech_tree.get_data(unit_type)  # type: TypeData

    if data.required_addons:
        addon = data.required_addons[0]
    else:
        addon = None

    for candidate in agent.unit_collection.get_group(PLAYER_SELF):  # type: PyUnit
        if candidate.unit_type in data.what_builds:
            if addon and not get_addon(agent, candidate).unit_type == addon:
                continue
            elif candidate.unit_type.is_building and candidate.is_training:
                continue
            elif not candidate.is_completed:
                continue
            elif candidate.unit_type.is_building and candidate.is_flying:
                continue
            elif isinstance(candidate.task, tasks.build.Build) or isinstance(candidate.task, tasks.train.Train):
                continue
            else:
                return candidate
    return None


def exists_producer_for(agent: BasicAgent, unit_type: Union[UnitType, UPGRADE_ID]) -> bool:
    # sourcery skip: use-any, use-next
    """
    A faster version of the function find_producer, it only looks if there is a unit which can build the given
    unit_type. It does not check if it is available or even done constructing.

    :return: True if there is a unit which might eventually build this unit, False otherwise.
    """

    # Internally SC has the wrong name of this unit. Band aid fix.
    if isinstance(unit_type, UPGRADE_ID) and unit_type == UPGRADE_ID.COMBATSHIELD:
        unit_type = UPGRADE_ID.SHIELDWALL

    what_builds = agent.tech_tree.get_data(unit_type).what_builds
    for py_unit in agent.unit_collection.get_group(PLAYER_SELF):  # type: PyUnit
        if py_unit.is_alive and py_unit.is_completed and py_unit.unit_type in what_builds:
            return True
    return False


def get_id(name: str) -> Optional[Union[UPGRADE_ID, UNIT_TYPEID]]:
    # sourcery skip: use-next
    """Returns the unit type/upgrade id of a unit with name 'name' (upper case no spaces)."""
    if name in UPGRADE_ID.__dict__.keys():
        return eval(f"UPGRADE_ID.{name}")

    for race in ["TERRAN", "PROTOSS", "ZERG"]:
        if f"{race}_{name}" in UNIT_TYPEID.__dict__.keys():
            return eval(f"UNIT_TYPEID.{race}_{name}")

    return None


def get_worker_type(agent: BasicAgent) -> Optional[UnitType]:
    """Returns the worker unit type of the current player race."""
    race = agent.get_player_race(PLAYER_SELF)
    if race == Race.Terran:
        return UnitType(UNIT_TYPEID.TERRAN_SCV, agent)
    if race == Race.Zerg:
        return UnitType(UNIT_TYPEID.ZERG_DRONE, agent)
    if race == Race.Protoss:
        return UnitType(UNIT_TYPEID.PROTOSS_PROBE, agent)
    return None


def has_prerequisites(agent: BasicAgent, unit_type: Union[UnitType, UPGRADE_ID]) -> bool:
    """Returns whether we have the required upgrades, addons, and units to build unit/upgrade."""
    data = agent.tech_tree.get_data(unit_type)
    if len(data.required_upgrades) + len(data.required_addons) + len(data.required_units) == 0:
        # No prerequisites required
        return True

    # data.required_upgrades: having ALL of these is required
    # There is currently no functionality in the API to check if we have an upgrade

    # data.required_units: owning ONE of these is required
    unit_typeids = {unit_type.unit_typeid for unit_type in data.required_units}
    py_units = list(
        agent.unit_collection.get_group(
            PLAYER_SELF,
            lambda u: u.is_completed and u.unit_type.unit_typeid in unit_typeids))

    # data.required_addons: a unit of this type must be present next to the producer
    addon_typeids = {unit_type.unit_typeid for unit_type in data.required_addons}
    addons = list(
        agent.unit_collection.get_group(
            PLAYER_SELF,
            lambda u: u.is_completed and u.unit_type.unit_typeid in addon_typeids))

    return (not unit_typeids or len(py_units) > 0) and (not addon_typeids or len(addons) > 0)


def unit_types_by_condition(agent: BasicAgent, condition: callable) -> set[UNIT_TYPEID]:
    """Returns all UNIT_TYPEIDs matching condition."""
    return {unit_typeid for unit_typeid in vars(UNIT_TYPEID).values() if
            isinstance(unit_typeid, UNIT_TYPEID) and condition(UnitType(unit_typeid, agent))}

@cache
def get_town_hall_unit_types(agent: BasicAgent) -> set[UnitType]:
    """Returns all town hall unit types."""
    return frozenset(UnitType(unit_type_id, agent) for unit_type_id in {UNIT_TYPEID.ZERG_HATCHERY, UNIT_TYPEID.TERRAN_COMMANDCENTER, UNIT_TYPEID.PROTOSS_NEXUS})


@singledispatch
def get_adjacent_neighbours(pos: Point2DI, agent: BasicAgent) -> list[Point2DI]:
    x = pos.x
    y = pos.y
    return [
        Point2DI(x - 1, y) if x > 0 else None,  # left
        Point2DI(x + 1, y) if x < agent.map_tools.width - 1 else None,  # right
        Point2DI(x, y - 1) if y > 0 else None,  # up
        Point2DI(x, y + 1) if y < agent.map_tools.height - 1 else None  # down
    ]

def get_all_neighbours(x, y):
    neighbours = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:  # Exclude the unit itself
                neighbours.append((x + dx, y + dy))
    return neighbours

@cache
def get_neighbours_within_distance(pos: Point2DI, distance: int = 3, ordered = False) -> tuple[Point2DI]:
    if not isinstance(pos, Point2DI):
        raise TypeError(f"pos must be of type Point2DI, not {type(pos)}")
    x = pos.x
    y = pos.y
    neighbours = set() if not ordered else [set() for _ in range(distance)]
    for dy in range(-distance, distance + 1):
        for dx in range(-distance, distance + 1):
            if dx != 0 or dy != 0:  # Exclude the unit itself
                nbr = Point2DI(x + dx, y + dy)
                if ordered:
                    index = max(abs(dx), abs(dy)) # [2, 3] -> 3, [1, 1] -> 2
                    index -= 1  # [3] -> [2] (since dist=3 -> [0,1,2]) 
                    neighbours[index].add(nbr)
                else:
                    neighbours.add(nbr)
    return frozenset(neighbours) if not ordered else tuple(neighbours)

@get_adjacent_neighbours.register(tuple)
def _(pos: tuple, agent: BasicAgent) -> list[tuple]:
    # {Point2DI(x, y), ...} -> {(x, y), ...}
    return set(map(lambda pos: (pos.x, pos.y), get_adjacent_neighbours(Point2DI(pos[0], pos[1]), agent)))


def get_units_in_radius(agent: BasicAgent,
                        position: Point2D,
                        radius: int,
                        condition: callable = lambda _: _) -> set[PyUnit]:
    """Returns a list of all units within a given radius of a given position.
    Optional parameter of condition to filter the units."""
    return agent.unit_collection.get_group(
        lambda unit: position.distance(unit.position) <= radius and condition(unit))

def get_enemies_in_neighbouring_tiles(agent: BasicAgent, tile_pos: Point2DI, fast: bool = False, dist = None) -> set[PyUnit]:
    """Returns a list of enemy units within a given radius of a given tile_position.
    Optional update of accurate to use get_all_units() instead of using unit collection."""
    neighbours = get_neighbours_within_distance(tile_pos, dist) if dist else get_neighbours_within_distance(tile_pos)
    if fast:
        pass
        # return {unit for unit in agent.get_all_units() if unit.tile_position in neighbours and unit.player == PLAYER_ENEMY}
    return agent.unit_collection.get_group(lambda unit: unit.tile_position in neighbours and unit.player == PLAYER_ENEMY and unit.can_attack)


def get_friendly_in_radius(agent: BasicAgent, position: Point2D, radius: int) -> set[PyUnit]:
    """Returns a list of friendly units within a given radius of a given position."""
    return get_units_in_radius(agent, position, radius, lambda unit: unit.player == PLAYER_SELF)


def get_enemies_in_radius(agent: BasicAgent, position: Point2D, radius: int) -> set[PyUnit]:
    """Returns a list of enemy units within a given radius of a given position."""
    return get_units_in_radius(agent, position, radius, lambda unit: unit.player == PLAYER_ENEMY)

def get_enemies_in_base_location(agent: BasicAgent, base_location: BaseLocation) -> set[PyUnit]:
    """Returns a list of enemy units within a given base location."""
    # alt: use agent.get_all_units()..
    return agent.unit_collection.get_group(lambda unit: base_location.contains_position(unit.position) and unit.player == PLAYER_ENEMY)


@cache
def get_enemy_start_pos(agent):
    return agent.base_location_manager.get_player_starting_base_location(PLAYER_ENEMY).position


@singledispatch
def get_closest(items: Iterable, cmp_pos: Point2D, access=lambda pos: pos):
    return min(items, key=lambda pos: cmp_pos.square_distance(access(pos)))


@cache
@get_closest.register
def _(items: frozenset, cmp_pos: Point2D, access=lambda pos: pos):  # maybe just Hashable
    return min(items, key=lambda pos: cmp_pos.square_distance(access(pos)))


def get_approx_distance(self, position):
    max_val = abs(self.x - position.x)
    min_val = abs(self.y - position.y)
    if max_val < min_val:
        min_val, max_val = max_val, min_val

    if min_val <= (max_val >> 2):
        return max_val

    min_calc = (3 * min_val) >> 3
    return (min_calc >> 5) + min_calc + max_val - (max_val >> 4) - (max_val >> 6)

def angle_to(from_pos, to_pos):
    dx = to_pos.x - from_pos.x
    dy = to_pos.y - from_pos.y
    direction = atan2(dy, dx)
    if direction < 0:
        direction += 2 * pi    # [-pi, pi] -> [0, 2pi] (to match Unit.facing)
    return direction


Point2D.square_distance = lambda self, other: (self.x - other.x) ** 2 + (self.y - other.y) ** 2
Point2D.__eq__ = lambda self, other: isinstance(
    other, Point2D) and self.square_distance(other) < 0.001 ** 2
Point2D.as_tuple = lambda self: (self.x, self.y)
Point2D.as_tile = lambda self: Point2DI(self)
Point2D.get_approx_distance = lambda self, other: get_approx_distance(self, other)
Point2D.distance = lambda self, other: sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
Point2D.__add__ = lambda self, other: Point2D(self.x + other.x, self.y + other.y)
Point2D.angle_to = lambda self, other: angle_to(self, other)
# Point2D.angle_to = lambda self, other: acos(self.dot(other) / (self.magnitude * other.magnitude))

Point2DI.square_distance = lambda self, other: (self.x - other.x) ** 2 + (self.y - other.y) ** 2
Point2DI.distance = lambda self, other: sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
Point2DI.__add__ = lambda self, other: Point2DI(self.x + other.x, self.y + other.y)
Point2DI.as_tuple = lambda self: (self.x, self.y)
Point2DI.get_approx_distance = lambda self, other: get_approx_distance(self, other)
Point2DI.as_tile = lambda self: self


BaseLocation.__repr__ = lambda self: f"<BaseLocation: {self.position}>"

Color.__floordiv__ = lambda self, s: Color(self.r // s, self.g // s, self.b // s)
