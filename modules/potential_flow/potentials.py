from __future__ import annotations
import math
from typing import TYPE_CHECKING
from pygame import Vector2
from modules.extra import point2d_to_tuple

from modules.potential_flow.regions import calculate_center
from library import Point2D

from modules.py_unit import PyUnit

if TYPE_CHECKING:
    from modules.potential_flow.flow_scout import PotentialFlowScout
    from agents.basic_agent import BasicAgent


# Enemy potential flow
# E(z) = p₅e^(-iα)N(z)
#        ps
def enemy_pf(enemy, scout_pos):
    if enemy.target:
        return needle_pval(enemy.position, scout_pos, enemy.target.position, (enemy.attack_range + 16) * 1.0 / enemy.radius) * ENEMY_NEEDLE * 2.5
    else:
        return source_potential(enemy.position, scout_pos) * ENEMY_NEEDLE * (enemy.attack_range) * (1.0 / enemy.radius)

# Like source/sink potential but the shape change to a direction
def needle_pval(scout, p, target, bias):
    if target == None:
        return Vector2()
    x = p.x() - scout.x()
    y = p.y() - scout.y()
    r2 = 1.0 * x * x + 1.0 * y * y

    V = Vector2(target.x() - scout.x(), target.y() - scout.y())
    v = Vector2(x, y)
    r = Vector2(x / r2, y / r2)

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
@point2d_to_tuple
def vortex_potential(scout, p):
    ic(scout)
    x = p[0] - scout[0]  # x - x_start
    y = p[1] - scout[1]  # y - y_start
    r2 = x * x + y * y  # (x-x_start)^2 + (y-y_start)^2
    return Vector2(y / r2, -x / r2)  # u, v


# S(z) = log(z-z_s)
@point2d_to_tuple
def source_potential(scout, p):
    x = p[0] - scout[0]
    y = p[1] - scout[1]
    r2 = 1.0 * x * x + y * y
    return Vector2(x / r2, y / r2)


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
def obstacle_potential(obs_pos, pos, center, a2):
    Ov = obstacle_vortex_potential(obs_pos, pos, center, a2)
    Os = obstacle_source_potential(obs_pos, pos, center, a2)

    if center.square_distance(pos) < DISTANCE_TO_SWITCH_SOURCE_SINK:
        return Ov * CENTER_VORTEX * 1.2 + Os * CENTER_SOURCE_SINK * 1.2
    else:
        return Ov * CENTER_VORTEX * 1.2 - Os * CENTER_SOURCE_SINK * 1.2


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
    return Vector2(vx, vy)


# O(z) = log(a^2/(z-Z)-conj(z_c-Z))
# s : obstacle position
# p : considered position
# c: center vortex position
def obstacle_source_potential(scout, p, c, a2):
    x = p[0] - scout[0]
    y = p[1] - scout[1]
    xc = c[0] - scout[0]
    yc = c[1] - scout[1]
    x2 = 1.0 * x * x
    y2 = 1.0 * y * y
    r2 = x2 + y2

    deno = r2 * (a2 * a2 - 2 * a2 * (x * xc + y * yc) + r2 * (xc * xc + yc * yc))

    vx = -a2 * (a2 * x - 2 * x * y * yc - x2 * xc + y2 * xc) / deno
    vy = -a2 * (a2 * y - 2 * x * y * xc - y2 * yc + x2 * yc) / deno

    return (vx, vy)
