from __future__ import annotations
import math
from typing import TYPE_CHECKING
from library import PLAYER_ENEMY, Point2D, Point2DI, UNIT_TYPEID, UnitType
from pygame import Vector2
from config import TIME_KEEP_ENEMY, TIME_KEEP_ENEMY_BUILDING
from modules.extra import unit_types_by_condition
from modules.potential_flow.flows_enum import (
    BORDER_SOURCE,
    BORDER_VORTEX,
    CENTER_SOURCE_SINK,
    CENTER_VORTEX,
    DISTANCE_TO_SWITCH_SOURCE_SINK,
    ENEMY_NEEDLE,
)
from modules.potential_flow.potentials import (
    enemy_pf,
    needle_pval,
    obstacle_potential,
    obstacle_source_potential,
    obstacle_vortex_potential,
    region_pf,
    source_potential,
    vortex_potential,
)
from modules.potential_flow.regions import calculate_center, get_base_locations_in_region, get_region, get_region_border, get_region_polygon

from modules.py_unit import PyUnit

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent


def update_flows(agent: BasicAgent) -> None:
    # agent.unit_collection.get_group(lambda unit: unit.unit_type.player == PLAYER_ENEMY and unit.unit_typeid == vechile):
    obstacles = set()
    for enemy in agent.unit_collection.get_group(PLAYER_ENEMY):
        # _list_o.push_back(make_pair((u)->getPosition(), ut.groundWeapon().maxRange()));\
        # obstacles.add((enemy.position, enemy.unit_type.attack_range))
        print(f"range: {enemy.unit_type.attack_range}")


def get_enemies_in_radius(agent, position: Point2D, radius: int) -> set[PyUnit]:
    """Returns a list of enemy units within a given radius of a given position."""
    # units_in_radius = []

    return agent.unit_collection.get_group(
        lambda unit: unit.unit_type.player == PLAYER_ENEMY
        and position.square_distance(unit.position) <= radius
    )

    """for enemy in agent.unit_collection.get_group(PLAYER_ENEMY):
        distance = position.distance(enemy.position)
        if distance <= radius:
            units_in_radius.append(enemy)

    return units_in_radius"""


def register_enemy_positions(enemies):
    for enemy in enemies:
        fade_time = (
            TIME_KEEP_ENEMY_BUILDING if enemy.unit_type.is_building else TIME_KEEP_ENEMY
        )

        # TODO: check if enemy is in bunker

        # TODO: update enemy position, in case Unit.position does not work

