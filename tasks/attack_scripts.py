from modules.py_unit import PyUnit
from typing import List

class AttackScripts:
    @staticmethod
    def attack_nearest(py_unit: PyUnit):
        """Attack the nearest enemy units."""
        print("attack nearest run")
        print(py_unit.radius)

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