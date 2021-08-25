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
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from py_unit import PyUnit
    from agents.basic_agent import BasicAgent

from tasks import build
from tasks import train
from library import UnitType, TypeData, PLAYER_SELF, Point2D, UPGRADE_ID, Point2DI, UNIT_TYPEID, Color, \
    BaseLocation, Race


def get_addon(agent: BasicAgent, candidate: PyUnit) -> Optional[PyUnit]:
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
            elif isinstance(candidate.task, build.Build) or isinstance(candidate.task, train.Train):
                continue
            else:
                return candidate
    return None


def exists_producer_for(agent: BasicAgent, unit_type: Union[UnitType, UPGRADE_ID]) -> bool:
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
    py_units = list(agent.unit_collection.get_group(PLAYER_SELF, lambda
        u: u.is_completed and u.unit_type.unit_typeid in unit_typeids))

    # data.required_addons: a unit of this type must be present next to the producer
    addon_typeids = {unit_type.unit_typeid for unit_type in data.required_addons}
    addons = list(agent.unit_collection.get_group(PLAYER_SELF, lambda
        u: u.is_completed and u.unit_type.unit_typeid in addon_typeids))

    return (len(unit_typeids) == 0 or len(py_units) > 0) and (len(addon_typeids) == 0 or len(addons) > 0)


def unit_types_by_condition(agent: BasicAgent, condition: callable) -> set[UNIT_TYPEID]:
    """Returns all UNIT_TYPEIDs matching condition."""
    return {unit_typeid for unit_typeid in vars(UNIT_TYPEID).values() if
            isinstance(unit_typeid, UNIT_TYPEID) and condition(UnitType(unit_typeid, agent))}


Point2D.square_distance = lambda self, other: (self.x - other.x) ** 2 + (self.y - other.y) ** 2
Point2D.__eq__ = lambda self, other: isinstance(other, Point2D) and self.square_distance(other) < 0.001 ** 2

Point2DI.square_distance = lambda self, other: (self.x - other.x) ** 2 + (self.y - other.y) ** 2
Point2DI.__add__ = lambda self, other: Point2DI(self.x + other.x, self.y + other.y)

BaseLocation.__repr__ = lambda self: f"<BaseLocation: {self.position}>"

Color.__floordiv__ = lambda self, s: Color(self.r // s, self.g // s, self.b // s)