from math import sqrt

from modules.py_unit import PyUnit
from typing import List
#from agents.basic_agent import BasicAgent
from library import PLAYER_ENEMY, Point2D


class AttackScripts:
    @staticmethod
    def attack_nearest(py_unit: PyUnit, agent):
        """Attack the nearest enemy units."""
        Point2D.distance = lambda self, other: sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

        pos = py_unit.position
        attack_range = int(py_unit.unit_type.attack_range)
        unit_list = agent.unit_collection.get_group(PLAYER_ENEMY, lambda u: u.unit_type.is_combat_unit)
        nearest_distance = 99999
        attack_unit = None

        for dx in range(-attack_range, attack_range + 1):
            for dy in range(-attack_range, attack_range + 1):
                # Calculate the target tile position within range
                target_tile_x = pos.x + dx
                target_tile_y = pos.y + dy

                for unit in unit_list:
                    if unit.position == (target_tile_x, target_tile_y):
                        if pos.distance(unit.position) < nearest_distance:
                            attack_unit = unit
                            nearest_distance = pos.distance(unit.position)
        if attack_unit:
            py_unit.attack_unit(attack_unit)
    @staticmethod
    def attack_lowest(py_unit: PyUnit):
        """Attack the enemy with the lowest health"""
        pass

    @staticmethod
    def kiting(py_unit: PyUnit):
        """Like attack_nearest but also keep the longest possible distance to enemy while weapon cooldown"""
        pass

    @staticmethod
    def attack_strongest(py_unit: PyUnit):
        """Like attack_nearest but focuses on the enemy with the strongest attack value"""
        pass

    @staticmethod
    def nok_av(py_unit: PyUnit):
        """Like attack_strongest but will NOT attack an enemy that have been dealt lethal attack on current step"""
        pass