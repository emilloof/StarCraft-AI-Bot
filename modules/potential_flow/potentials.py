from __future__ import annotations
import math
from typing import TYPE_CHECKING
from modules.extra import point2d_to_tuple

from modules.potential_flow.regions import calc_center
from library import Point2D
from modules.potential_flow.vector import Vector

from modules.py_unit import PyUnit

if TYPE_CHECKING:
    from modules.potential_flow.flow_scout import PotentialFlowScout


# Enemy potential flow
# E(z) = p₅e^(-iα)N(z)
#        ps
def enemy_pf(ENEMY_NEEDLE, scout_pos: Point2D, enemy: PyUnit):
    # Create a vector that represents the direction the unit is looking at
    range_used = enemy.unit_type.attack_range # (attack_range vs sight_range)?. prob use attackrange since scv.attack_range = 0.1, but marine.attack_range = 5
    target_x = enemy.position.x + range_used * math.cos(enemy.facing)
    target_y = enemy.position.y + range_used * math.sin(enemy.facing)
    target = Point2D(target_x, target_y)

    enemy.approx_target = target

    return ENEMY_NEEDLE * needle_pval(enemy.position, scout_pos, target, enemy.unit_type.attack_range * 1.0 / enemy.radius) * 2.5 # vene om ska ha 2.5 *

# Like source/sink potential but the shape change to a direction
def needle_pval(source, point, target, bias):
    if target == None:
        return Vector()
    x = point.x - source.x
    y = point.y - source.y
    r2 = 1.0 * x * x + 1.0 * y * y

    V = Vector(target.x - source.x, target.y - source.y)
    v = Vector(x, y)
    r = Vector(x / r2, y / r2)

    if not V: # maybe should use enemy.has_target instead
        return Vector()

    # cos(anpha)
    cosn = 1 / bias
    # cos(theta)
    cost = V.cos(v)

    if cost >= cosn:
        sinn = math.sqrt(1 - cosn * cosn)
        sint = V.sin(v)
        t = 1
        if sint >= 0:
            # 1/cos(anpha - theta)
            r *= 1 / (cosn * cost + sinn * sint)
        else:
            # 1/cos(-anpha - theta)
            r *= 1 / (cosn * cost - sinn * sint)

    return r


# V(z) = ilog(z-z_start)
# s=curReg_center, p=enemy_position
# @point2d_to_tuple
def vortex_potential(source, point):
    # ic(source)
    x = point.x - source.x  # x - x_start
    y = point.y - source.y  # y - y_start
    r2 = x * x + y * y  # (x-x_start)^2 + (y-y_start)^2
    return Vector(y / r2, -x / r2)  # u, v


# S(z) = log(z-z_s)
# @point2d_to_tuple
def source_potential(source, point):
    x = point.x - source.x
    y = point.y - source.y
    r2 = 1.0 * x * x + y * y
    return Vector(x / r2, y / r2)


# R(z) = p₁V(z) + p₂S(z) if ||z'|| > dᵣ_ₜₕᵣₑₛ
#        p₁V(z) - p₂S(z) otherwise
def region_pf(region_center, pos, center, scout: PotentialFlowScout, vortex_correction, source_correction, d_r_thres):
    p1Vz = vortex_potential(region_center, pos) * scout.CENTER_VORTEX * vortex_correction
    p2Sz = source_potential(region_center, pos) * scout.CENTER_SOURCE_SINK * source_correction
    if center < d_r_thres:
        return p1Vz + p2Sz
    else:
        return p1Vz - p2Sz



# Obstacle potential flow
# O(z) = p₁Oᵥ(z) + p₂Oₛ(z) if ||z꜀'|| > dᵣ_ₜₕᵣₑₛ
#        p₁Oᵥ(z) - p₂Oₛ(z) otherwise
def obstacle_potential(scout: PotentialFlowScout, obs_pos, pos, center, a2):
    Ov = obstacle_vortex_potential(obs_pos, pos, center, a2)
    Os = obstacle_source_potential(obs_pos, pos, center, a2)

    if center.square_distance(pos) < scout.DISTANCE_TO_SWITCH_SOURCE_SINK:
        return Ov * scout.CENTER_VORTEX * 1.2 + Os * scout.CENTER_SOURCE_SINK * 1.2
    else:
        return Ov * scout.CENTER_VORTEX * 1.2 - Os * scout.CENTER_SOURCE_SINK * 1.2


# Circle theorem obstacle by a vortex O(z) = -ilog(a^2/(z-Z)-conj(z_c-Z))
# s : obstacle position
# p : considered position
# c: center vortex position
def obstacle_vortex_potential(obs_pos, pos, center, a2):
    x = pos.x - obs_pos.x
    y = pos.y - obs_pos.y
    xc = center.x - obs_pos.x
    yc = center.y - obs_pos.y
    x2 = 1.0 * x * x
    y2 = 1.0 * y * y
    r2 = x2 + y2
    deno = r2 * (a2 * a2 - 2 * a2 * (x * xc + y * yc) + r2 * (xc * xc + yc * yc))
    vx = a2 * (a2 * y - 2 * x * y * xc - y2 * yc + x2 * yc) / deno
    vy = -a2 * (a2 * x - 2 * x * y * yc - x2 * xc + y2 * xc) / deno
    return Vector(vx, vy)


# O(z) = log(a^2/(z-Z)-conj(z_c-Z))
# s : obstacle position
# p : considered position
# c: center vortex position
def obstacle_source_potential(scout, p, c, a2):
    x = p.x - scout.x
    y = p.y - scout.y
    xc = c.x - scout.x
    yc = c.y - scout.y
    x2 = 1.0 * x * x
    y2 = 1.0 * y * y
    r2 = x2 + y2

    deno = r2 * (a2 * a2 - 2 * a2 * (x * xc + y * yc) + r2 * (xc * xc + yc * yc))

    vx = -a2 * (a2 * x - 2 * x * y * yc - x2 * xc + y2 * xc) / deno
    vy = -a2 * (a2 * y - 2 * x * y * xc - y2 * yc + x2 * yc) / deno

    return Vector(vx, vy)
