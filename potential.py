from __future__ import annotations
import math
from typing import TYPE_CHECKING
from library import PLAYER_ENEMY, Point2D
from pygame import Vector2

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



def get_units_in_radius(agent, position: Point2D, radius: int) -> list:
    """Returns a list of enemy units within a given radius of a given position."""
    units_in_radius = []

    Point2D.distance = lambda self, other: math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    for enemy in agent.unit_collection.get_group(PLAYER_ENEMY):
            distance = position.distance(enemy.position)
            if distance <= radius:
                units_in_radius.append(enemy)

    return units_in_radius

# V(z) = iUlog(z-z_start)
#-Gamma/2pi * ln(sqrt((x-x0)^2+(y-y0)^2))
def vortex_potential(s, p):
    x = p[0] - s[0]
    y = p[1] - s[1]
    r2 = x*x + y*y
    return (y/r2, -x/r2)