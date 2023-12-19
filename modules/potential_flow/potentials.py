from __future__ import annotations
import math
from typing import TYPE_CHECKING
from library import Color, Point2D, Point2DI, UNIT_TYPEID
from config import DEBUG_SCOUT, OLD_ENEMIES_ENABLED
from modules.extra import get_closest, get_enemies_in_neighbouring_tiles, get_enemies_in_radius
from config import DEBUG_SCOUT

from modules.potential_flow.flows import (
    enemy_pf,
    obstacle_potential,
    region_pf,
    source_potential,
    vortex_potential,
)
from modules.potential_flow.regions import Region
from modules.potential_flow.vector import Vector

from modules.py_unit import PyUnit

if TYPE_CHECKING:
    from tasks.pf_scout import PFscout

# Start from center of the region and the combine of source and vortex potential flow


def region_pval(scout: PFscout, scout_unit: PyUnit, target_region: Region) -> Vector:
    cur_reg = scout.agent.region_manager.get_region(scout_unit.tile_position)
    cur_reg_center = cur_reg.center
    d2_center = cur_reg_center.distance(scout_unit.position)

    source_correction = 1 if cur_reg == target_region else 0
    vortex_correction = 1 if cur_reg == target_region else 0.01 \
        if d2_center < scout.DISTANCE_TO_SWITCH_SOURCE_SINK else 0.01
    scout.DISTANCE_TO_SWITCH_SOURCE_SINK = scout_unit.unit_type.sight_range + 1

    if DEBUG_SCOUT:
        scout.region_potentials.clear()
        _vrtx_potential = vortex_potential(cur_reg_center, scout_unit.position) \
            * scout.CENTER_VORTEX * vortex_correction
        scout.region_potentials.append(_vrtx_potential)    # * 100

        _src_potential = source_potential(cur_reg_center, scout_unit.position) \
            * scout.CENTER_SOURCE_SINK * source_correction

        scout.region_potentials.append(
            _src_potential
            if d2_center < scout.DISTANCE_TO_SWITCH_SOURCE_SINK else -_src_potential)    # * 100

        # pull_correction = 0 if cur_reg == target_region else 20 # 20
        # t_sor = source_potential(center, scout_unit.position)
        #    * scout.CENTER_SOURCE_SINK * pull_correction
        # scout.region_potentials.append(-t_sor * 100)
    
    return region_pf(cur_reg_center, scout_unit.position, d2_center, scout, vortex_correction,
                     source_correction, scout.DISTANCE_TO_SWITCH_SOURCE_SINK)


def border_pval(scout: PFscout, scout_unit: PyUnit, cur_region: Region, target_reg: Region,
                is_different_region: bool):
    # border = get_region_polygon(cur_region) idk if needed *
    detail_border: frozenset[Point2DI] = cur_region.border
    scout_position = scout_unit.position

    border_co = len(detail_border) / (math.pi * 14)
    scout.DISTANCE_TO_ACTIVE_BORDER_FLOW = max(border_co, 3)
    src_correction = 1 \
        if scout.agent.region_manager.get_region(scout_unit.tile_position) == target_reg else 0
    chokepoint = get_closest(scout.agent.region_manager.chokepoints_as_centers, scout_position)
    inactive_border = scout_position.distance(chokepoint) < scout.DISTANCE_TO_ACTIVE_BORDER_FLOW + 4

    num_border = 0
    b_val = Vector()

    if DEBUG_SCOUT:
        list_border = []

    for border_tile in detail_border:
        if scout_position.distance(border_tile) < scout.DISTANCE_TO_ACTIVE_BORDER_FLOW:
            if is_different_region and inactive_border:
                continue

            vrtx = vortex_potential(border_tile, scout_position) * scout.BORDER_VORTEX
            src = source_potential(border_tile,
                                   scout_position) * scout.BORDER_SOURCE * src_correction

            if DEBUG_SCOUT:
                list_border.append(vrtx + src)  # * 100
                scout.agent.map_tools.draw_circle(Point2D(border_tile), 2, Color.PURPLE)  # Color.RED

            b_val += vrtx + src
            num_border += 1
    # TODO: handle border holes (if exist, dont think they do)

    if DEBUG_SCOUT:
        if list_border:
            scout.border_potentials = list_border
    return b_val


def attract_point_pval(scout: PFscout, scout_unit: PyUnit):
    re = Vector()
    pos = scout_unit.position
    for p in scout.attract_points:
        if DEBUG_SCOUT:
            scout.region_potentials.append(source_potential(p, pos) * (-32))    # * 100
            scout.agent.map_tools.draw_text(p, "at", Color(255, 165, 0))  # orange
        re += source_potential(p, pos) * (-32)
    return re


# Unit's (building and enemy) emitted potential flow
# Rotate an (-anpha) angle. Input is the anpha angle
def unit_pval(scout: PFscout, enemy: PyUnit, scout_unit: PyUnit):
    enemy_type = enemy.unit_type
    scout_pos = scout_unit.position
    region = scout.agent.region_manager.get_region(scout_unit.tile_position)
    center = None

    if DEBUG_SCOUT:
        up = enemy.position
        scout.agent.map_tools.draw_box(Point2D(up.x - enemy.radius, up.y - enemy.radius),
                                   Point2D(up.x + enemy.radius, up.y + enemy.radius), Color.GREEN)

    if region:    # if prob not needed
        center = region.center

    # Unit's radius
    enemy_radius = enemy.radius

    def get_direction(from_pos, to_pos):
        dx = to_pos.x - from_pos.x
        dy = to_pos.y - from_pos.y
        direction = math.atan2(dy, dx)
        if direction < 0:
            direction += 2 * math.pi    # [-pi, pi] -> [0, 2pi] (to match Unit.facing)
        return direction

    if enemy_type.is_geyser or enemy_type.is_mineral or enemy_type.is_geyser:    # is invincible
        # Mineral and other indestructive obstacle
        return obstacle_potential(scout, enemy.position, scout_pos, center,
                                  enemy_radius * enemy_radius)

    elif (enemy_type.is_building and not enemy.is_flying
          and (not enemy_type.is_combat_unit or enemy.is_being_constructed)
          and enemy_type.unit_typeid != UNIT_TYPEID.TERRAN_BUNKER):

        return obstacle_potential(scout, enemy.position, scout_pos, center,
                                  enemy_radius * enemy_radius)
    # need bunker handling?
    elif enemy.can_attack and enemy.position.distance(scout_pos) < enemy_type.attack_range + 4 \
        and ((enemy_target := enemy.get_target()) == scout_unit or not enemy_type.is_worker):
        # If is can ttacking enemy unit or worker who aim at our scout's position

        attack_range = enemy_type.attack_range + 1
        if enemy_target == scout_unit:
            return enemy_pf(scout.ENEMY_NEEDLE, scout_pos, enemy, enemy_target, attack_range)
        else:
            return source_potential(enemy.position, scout_pos) * scout.ENEMY_NEEDLE \
                * (enemy.unit_type.attack_range - 0.5) * (1.0 / enemy.radius)
    elif not (enemy_type.is_combat_unit) and (enemy.is_flying or enemy.is_burrowed):
        return Vector()
    # else
    return obstacle_potential(scout, enemy.position, scout_pos, center, enemy_radius * enemy_radius)


def calculate_pval(scout: PFscout, scout_unit: PyUnit):
    cur_region = scout.agent.region_manager.get_region(scout_unit.tile_position)

    pval = Vector()

    enemy_direction = Vector()
    enemy_num = 0
    obstacle_val = Vector()
    obstacle_num = 0

    if DEBUG_SCOUT:
        units = []
        obstacles = set()

    # Visible and invisible enemy units
    # .union(scout.agent.unit_collection.get_old_enemies())
    """ TODO: * now its getting enemies in radius and previously
    seen enemies (REGARDLESS OF RADIUS):
    so prob wrong"""
    
    enemies = (
        get_enemies_in_neighbouring_tiles(
            scout.agent, scout_unit.tile_position, fast=False, dist=scout_unit.unit_type.sight_range + 2
        )
        if not OLD_ENEMIES_ENABLED
        else get_enemies_in_radius(
            scout.agent, scout_unit.position, scout_unit.unit_type.sight_range + 2
        )
    )
    scout.register_enemy_positions(enemies)

    # Calculate unitPVal
    for enemy in scout.get_enemies():
        enemy_pval = unit_pval(scout, enemy, scout_unit)
        # _ = enemy.target
        if (enemy.can_attack
                and (not enemy.unit_type.is_worker or enemy.get_target() == scout_unit)):
            enemy_direction += enemy_pval
            enemy_num += 1
            pval += enemy_pval

            if DEBUG_SCOUT:
                pass
                # obstacles.add((enemy, enemy.unit_type.attack_range))

        else:
            # obstacle
            obstacle_num += 1
            obstacle_val += enemy_pval

            if DEBUG_SCOUT:
                obstacles.add((enemy, enemy.radius))

        if DEBUG_SCOUT:
            if enemy_pval:
                units.append(enemy_pval)    # * 100

    # Add back obstacle value after averaged
    if obstacle_num:
        pval += obstacle_val * (1.0 / obstacle_num)

    if DEBUG_SCOUT:
        if units:
            scout.unit_potentials = units
        if obstacles:
            scout.obstacles_debug = obstacles
        all_potentials = [pval]

    # Calculate regionPVal
    region_val = region_pval(scout, scout_unit, scout.target_region)
    pval += region_val
    if DEBUG_SCOUT:
        all_potentials.append(region_val) # * 100

    # Calculate borderPVal
    curr_border_pval = border_pval(scout, scout_unit, cur_region, scout.target_region, cur_region
                                   != scout.target_region)
    if scout.use_border:
        pval += curr_border_pval

    if DEBUG_SCOUT:
        all_potentials.append(
            curr_border_pval)    # _all_potentials_ithink.append(curr_border_pval * 100)
        scout.all_potentials = all_potentials

    if scout.USE_ATTRACT_PVAL:
        att_tmp = attract_point_pval(scout, scout_unit)
        pval += att_tmp
    else:
        att_tmp = Vector()

    # Checking if enemy infront of us
    if enemy_direction.length() > 0:
        # testing two values since og code for cos_enemy did not work as intended
        og_cos_enemy = enemy_direction.cos(region_val)
        _cos_enemy = enemy_direction.cos(
            Vector(math.cos(scout_unit.facing), math.sin(scout_unit.facing)))
        coses = [og_cos_enemy]    # , _cos_enemy]
        for cos_enemy in coses:
            if (cos_enemy < -0.5 and enemy_num >= 3) or (cos_enemy < -0.85) \
                    or curr_border_pval.cos(att_tmp) < -0.5:
                # reverse vals
                if DEBUG_SCOUT:
                    ic("scout REVERSE!")
                # THIS DOES NOT WORK, TODO: FIX *
                #if scout.agent.current_frame - scout.last_reverse_frame > 10:
                if True:
                    scout.last_reverse_frame = scout.agent.current_frame
                    scout.go *= -1
                break

    return pval
