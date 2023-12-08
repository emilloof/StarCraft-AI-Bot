from __future__ import annotations
import math
from typing import TYPE_CHECKING
from library import PLAYER_ENEMY, Color, Point2D, Point2DI, UNIT_TYPEID
from modules.extra import get_closest, get_enemies_in_radius

from modules.potential_flow.potentials import (
    enemy_pf,
    obstacle_potential,
    region_pf,
    source_potential,
    vortex_potential,
)
from modules.potential_flow.regions import Region, get_region
from modules.potential_flow.vector import Vector

from modules.py_unit import PyUnit

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent
    from modules.potential_flow.flow_scout import PotentialFlowScout


def update_flows(agent: BasicAgent) -> None:
    obstacles = set()
    for enemy in agent.unit_collection.get_group(PLAYER_ENEMY):
        print(f"range: {enemy.unit_type.attack_range}")

# Start from center of the region and the combine of source and vortex potential flow


def region_pval(agent: BasicAgent, target_region: Region,
                scout: PotentialFlowScout, scout_unit: PyUnit) -> Vector:
    center = target_region.center
    if base_locations := target_region.base_locations:
        center = base_locations[0].position
    cur_reg = get_region(agent, scout_unit.tile_position)
    cur_reg_center = cur_reg.center
    d2_center = cur_reg_center.distance(scout_unit.position)

    source_correction = 1 if cur_reg == target_region else 0
    vortex_correction = 1 if cur_reg == target_region else 0.01 if d2_center < scout.DISTANCE_TO_SWITCH_SOURCE_SINK else 0.01
    # unsure bout dis ↓
    scout.DISTANCE_TO_SWITCH_SOURCE_SINK = scout_unit.unit_type.sight_range + 1

    # DEBUG
    scout.region_potentials.clear()
    scout.region_potentials.append(
        vortex_potential(
            cur_reg_center,
            scout_unit.position) *
        scout.CENTER_VORTEX *
        vortex_correction)  # * 100

    if d2_center < scout.DISTANCE_TO_SWITCH_SOURCE_SINK:
        # fmt: off
        scout.region_potentials.append(source_potential(cur_reg_center, scout_unit.position) * scout.CENTER_SOURCE_SINK * source_correction) # 100
    else:
        scout.region_potentials.append(-source_potential(cur_reg_center, scout_unit.position) * scout.CENTER_SOURCE_SINK * source_correction) # 100

    # pull_correction = 0 if cur_reg == target_region else 20 # 20
    # t_sor = source_potential(center, scout_unit.position) * scout.CENTER_SOURCE_SINK * pull_correction
    # scout.region_potentials.append(-t_sor * 100)
    # DEBUG

    return region_pf(cur_reg_center, scout_unit.position, d2_center, scout, vortex_correction, source_correction, scout.DISTANCE_TO_SWITCH_SOURCE_SINK)


def border_pval(agent: BasicAgent, cur_region, scout: PotentialFlowScout, scout_unit: PyUnit, target_reg, is_different_region):
    # border = get_region_polygon(cur_region) idk if needed *
    detail_border: list[Point2DI] = cur_region.border
    scout_position = scout_unit.position

    num_border = 0
    b_val = Vector()
    border_co = len(detail_border)/(math.pi * 14)
    _temp_border_val = 3 # 96 before
    scout.DISTANCE_TO_ACTIVE_BORDER_FLOW = border_co if border_co > _temp_border_val else _temp_border_val
    source_correction = 1 if get_region(agent, scout_unit.tile_position) == target_reg else 0
    chokepoint = get_closest(scout_position, agent.chokepoints, lambda pos: pos[1])[1]
    inactive_border = scout_position.distance(chokepoint) < scout.DISTANCE_TO_ACTIVE_BORDER_FLOW + 4 # 128

    # DEBUG
    list_border = list()
    # DEBUG

    for border_tile in detail_border:
        if scout_position.distance(border_tile) < scout.DISTANCE_TO_ACTIVE_BORDER_FLOW:
            if is_different_region and inactive_border:
                continue

            # DEBUG
            # * 100: list_border.append(vortex_potential(border_tile, scout_position)*scout.BORDER_VORTEX*100 + source_potential(border_tile, scout_position)*scout.BORDER_SOURCE*100*source_correction)
            list_border.append(vortex_potential(border_tile, scout_position)*scout.BORDER_VORTEX + source_potential(border_tile, scout_position)*scout.BORDER_SOURCE*source_correction)
            agent.map_tools.draw_circle(Point2D(border_tile), 2, Color.PURPLE) # Color.RED
            # DEBUG

            b_val += vortex_potential(border_tile, scout_position)*scout.BORDER_VORTEX + source_potential(border_tile, scout_position)*scout.BORDER_SOURCE*source_correction
            num_border += 1
    # TODO: handle border holes (if exist, dont think they do)

    # DEBUG
    if list_border:
        scout.border_potentials = list_border
    # DEBUG
    return b_val


def attract_point_pval(scout: PotentialFlowScout, scout_unit: PyUnit):
    # Implementation of the attractPointPVal function
    re = Vector()
    pos = scout_unit.position
    for p in scout.attract_points:
            # DEBUG
            # * 100: scout.region_potentials.append(source_potential(p, pos)*(-1000)*100)
        scout.region_potentials.append(source_potential(p, pos)*(-32))  # -1000
        # DEBUG
        re += source_potential(p, pos)*(-32)  # -1000
    return re


# Unit's (building and enemy) emitted potential flow
# Rotate an (-anpha) angle. Input is the anpha angle
def unit_pval(scout: PotentialFlowScout, enemy: PyUnit, scout_unit: PyUnit):
    enemy_type = enemy.unit_type
    scout_pos = scout_unit.position
    region = get_region(scout.agent, scout_unit.tile_position)
    center = None

    # DEBUG
    up = enemy.position
    scout.agent.map_tools.draw_box(Point2D(up.x-enemy.radius, up.y-enemy.radius), Point2D(up.x+enemy.radius, up.y+enemy.radius), Color.GREEN)
    # DEBUG

    if region:  # if prob not needed
        center = region.center

    # Unit's radius
    enemy_radius = enemy.radius

    def get_direction(from_pos, to_pos):
        dx = to_pos.x - from_pos.x
        dy = to_pos.y - from_pos.y
        direction = math.atan2(dy, dx)
        if direction < 0:
            direction += 2 * math.pi  # [-pi, pi] -> [0, 2pi] (to match Unit.facing)
        return direction

    if enemy_type.is_geyser or enemy_type.is_mineral or enemy_type.is_geyser:  # enemy.isInvincible():
        # Mineral and other indestructive obstacle
        return obstacle_potential(scout, enemy.position, scout_pos, center, enemy_radius * enemy_radius)

        # return vortexPotential(u->getPosition(), p)*_p[6];
    elif enemy_type.is_building and not enemy.is_flying and (not enemy_type.is_combat_unit or enemy.is_being_constructed) \
        and enemy_type.unit_typeid != UNIT_TYPEID.TERRAN_BUNKER:

        return obstacle_potential(scout, enemy.position, scout_pos, center, enemy_radius * enemy_radius)
    # need bunker handling?
    elif enemy_type.is_combat_unit and (not enemy_type.is_worker or enemy.target == scout_unit) \
        and enemy.position.distance(scout_pos) < enemy_type.attack_range + 4: # or use can_attack_ground instead?
        # If is can ttacking enemy unit or worker who aim at our scout's position

        enemy_direction = get_direction(enemy.position, scout_pos)
        if abs(enemy.facing - enemy_direction) < 0.6: # half a radian?
            # The enemy is facing the scout # (enemy.target and enemy.has_target) - does not work.. :(
            return enemy_pf(scout.ENEMY_NEEDLE, scout_pos, enemy)
        else:
            return source_potential(enemy.position, scout_pos) * scout.ENEMY_NEEDLE * (enemy.unit_type.attack_range - 0.5) * (1.0 / enemy.radius)
    elif not (enemy_type.is_combat_unit) and (
        enemy.is_flying or enemy.is_burrowed): # enemy.isLifted()
        return Vector()
    # else
    return obstacle_potential(scout, enemy.position, scout_pos, center, enemy_radius * enemy_radius)


def calculate_pval(scout: PotentialFlowScout, scout_unit: PyUnit):
    cur_region = get_region(scout.agent, scout_unit.tile_position)

    pval = Vector()

    enemy_direction = Vector()
    enemy_num = 0
    obstacle_val = Vector()
    obstacle_num = 0

    # DEBUG
    units = []
    all_potentials = []
    obstacles = set()
    # DEBUG

    # Visible and invisible enemy units
    enemies = get_enemies_in_radius(scout.agent, scout_unit.position, scout_unit.unit_type.sight_range + 2
    ) # .union(scout.agent.unit_collection.get_old_enemies()) # TODO: * now its getting enemies in radius and previously seen enemies (REGARDLESS OF RADIUS): so prob wrong
    # enemy_positions = register_enemy_positions(all_enemies)
    scout.register_enemy_positions(enemies)

    # Calculate unitPVal
    for enemy in scout.get_enemies():
        enemy_pval = unit_pval(scout, enemy, scout_unit)
        if enemy.unit_type.is_combat_unit and (not enemy.unit_type.is_worker or enemy.approx_target.distance(scout_unit) < 0.5):
            enemy_direction += enemy_pval
            enemy_num += 1
            pval += enemy_pval

            # DEBUG
            obstacles.add((enemy, enemy.unit_type.attack_range))
            # DEBUG

        else:
            # obstacle
            obstacle_num += 1
            obstacle_val += enemy_pval

            # DEBUG
            obstacles.add((enemy, enemy.radius))
            # DEBUG

        # DEBUG
        if enemy_pval:
            units.append(enemy_pval * 100)
        # DEBUG

    # Add back obstacle value after averaged
    if obstacle_num:
        pval += obstacle_val * (1.0 / obstacle_num)

    # DEBUG
    if units:
        scout.unit_potentials = units
    if obstacles:
        scout.obstacles_debug = obstacles
    all_potentials.append(pval) # _all_potentials_ithink.append(pval * 100)
    # DEBUG

    # Calculate regionPVal
    region_val = region_pval(scout.agent, scout.target_region, scout, scout_unit)
    pval += region_val
    # DEBUG
    all_potentials.append(region_val) # _all_potentials_ithink.append(region_val * 100)
    # DEBUG

    # Calculate borderPVal
    curr_border_pval = border_pval(scout.agent, cur_region, scout, scout_unit, scout.target_region, cur_region != scout.target_region)
    if scout.use_border:
        pval += curr_border_pval

    # DEBUG
    all_potentials.append(curr_border_pval) # _all_potentials_ithink.append(curr_border_pval * 100)
    scout.all_potentials = all_potentials
    # DEBUG

    att_tmp = attract_point_pval(scout, scout_unit)
    pval += att_tmp

    # Checking if enemy infront of us
    if enemy_direction.length() > 0:
        # testing two values since og code for cos_enemy did not work as intended
        og_cos_enemy = enemy_direction.cos(region_val)    #cos_enemy = enemy_direction.cos(region_val)
        _cos_enemy = enemy_direction.cos(Vector(math.cos(scout_unit.facing), math.sin(scout_unit.facing)))
        coses = [og_cos_enemy, _cos_enemy]
        for cos_enemy in coses:
            if (cos_enemy < -0.5 and enemy_num >= 3) or (cos_enemy < -0.85) \
              or curr_border_pval.cos(att_tmp) < -0.5:
                # reverse vals
                ic("REVERSE!")
                scout.go *= -1
                break

    return pval
