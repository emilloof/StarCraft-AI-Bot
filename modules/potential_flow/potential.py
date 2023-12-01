from __future__ import annotations
import math
from typing import TYPE_CHECKING
from library import PLAYER_ENEMY, Point2D, Point2DI, UNIT_TYPEID, UnitType
from pygame import Vector2
from config import TIME_KEEP_ENEMY, TIME_KEEP_ENEMY_BUILDING
from modules.extra import get_enemies_in_radius, unit_types_by_condition

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
    from modules.potential_flow.flow_scout import PotentialFlowScout


def update_flows(agent: BasicAgent) -> None:
    # agent.unit_collection.get_group(lambda unit: unit.unit_type.player == PLAYER_ENEMY and unit.unit_typeid == vechile):
    obstacles = set()
    for enemy in agent.unit_collection.get_group(PLAYER_ENEMY):
        # _list_o.push_back(make_pair((u)->getPosition(), ut.groundWeapon().maxRange()));\
        # obstacles.add((enemy.position, enemy.unit_type.attack_range))
        print(f"range: {enemy.unit_type.attack_range}")


# Start from center of the region and the combine of source and vortex potential flow
def region_pval(agent: BasicAgent, target_region, scout: PotentialFlowScout, scout_unit: PyUnit) -> Vector2:
    # Implementation of the regionPVal function
    center = calculate_center(target_region)
    base_locations = get_base_locations_in_region(agent, target_region)
    if base_locations:
        center = base_locations[0].position
    cur_reg = get_region(agent, agent.regions, scout_unit.tile_position)
    cur_reg_center = calculate_center(cur_reg)
    d2_center = cur_reg_center.square_distance(scout_unit.position)

    source_correction = 1 if cur_reg == target_region else 0
    vortex_correction = 1 if cur_reg == target_region else 0.01 if d2_center < scout.DISTANCE_TO_SWITCH_SOURCE_SINK else 0.01
    # unsure bout dis ↓
    scout.DISTANCE_TO_SWITCH_SOURCE_SINK = scout_unit.unit_type.sight_range + 32

    return region_pf(cur_reg_center, scout_unit.position, d2_center, scout, vortex_correction, source_correction, scout.DISTANCE_TO_SWITCH_SOURCE_SINK)
