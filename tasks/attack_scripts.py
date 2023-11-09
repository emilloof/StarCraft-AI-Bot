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
        myX = pos.x
        myY = pos.y
        attack_range = py_unit.unit_type.attack_range
        unit_list = agent.unit_collection.get_group(PLAYER_ENEMY, lambda u: u.unit_type.is_combat_unit)
        nearest_distance = 99999
        attack_unit = None

        for pyunit in unit_list:
            if (myX - attack_range) < pyunit.position.x < (myX + attack_range) and (
                        myY - attack_range) < pyunit.position.y < (myY + attack_range):

                if pos.distance(pyunit.position) < nearest_distance:
                    attack_unit = pyunit.unit
                    nearest_distance = pos.distance(pyunit.position)
        if attack_unit:
            py_unit.unit.attack_unit(attack_unit)

    @staticmethod
    def attack_lowest(py_unit: PyUnit, agent):
        """Attack the enemy with the lowest health"""
        pos = py_unit.position
        myX = pos.x
        myY = pos.y
        attack_range = py_unit.unit_type.attack_range
        unit_list = agent.unit_collection.get_group(PLAYER_ENEMY, lambda u: u.unit_type.is_combat_unit)
        lowest_attack = 0
        attack_unit = None

        for unit in unit_list:
            if (myX - attack_range) < unit.position.x < (myX + attack_range) and (myY -attack_range) < unit.position.y < (myY + attack_range):
                if unit.hit_points > lowest_attack: #WROOOOOOOOOOOOOOOOOOOOOOONG
                    attack_unit = unit.unit
        if attack_unit:
            py_unit.unit.attack_unit(attack_unit)

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