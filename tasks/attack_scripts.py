from math import sqrt
from modules.py_unit import PyUnit
from library import PLAYER_ENEMY, Point2D


class AttackScripts:
    @staticmethod
    def attack_nearest(py_unit: PyUnit, agent):
        """Attack the nearest enemy units."""
        AttackScripts.general_loop("attack_nearest", py_unit, agent)

    @staticmethod
    def attack_lowest(py_unit: PyUnit, agent):
        """Attack the enemy with the lowest health."""
        AttackScripts.general_loop("attack_lowest", py_unit, agent)

    @staticmethod
    def kiting(py_unit: PyUnit, agent):
        """Like attack_nearest but also keep the longest possible distance to enemy while weapon cooldown."""
        AttackScripts.general_loop("kiting", py_unit, agent)

    @staticmethod
    def attack_strongest(py_unit: PyUnit, agent):
        """Like attack_nearest but focuses on the enemy with the strongest attack value."""
        AttackScripts.general_loop("attack_strongest", py_unit, agent)

    @staticmethod
    def nok_av(py_unit: PyUnit, agent):
        """Like attack_strongest but will NOT attack an enemy that have been dealt lethal attack on current step."""
        pos = py_unit.position
        attack_range = py_unit.unit_type.attack_range
        unit_list = agent.unit_collection.get_group(PLAYER_ENEMY, lambda u: u.unit_type.is_combat_unit)
        strongest_attack = 0
        attack_unit = None

        for pyunit in unit_list:
            if pos.distance(pyunit.position) <= attack_range:
                if pyunit.unit_type.attack_damage > strongest_attack and pyunit.hp > 0:
                    attack_unit = pyunit
                    strongest_attack = pyunit.unit_type.attack_damage

        if attack_unit:
            py_unit.unit.attack_unit(attack_unit.unit)
            attack_unit.hp = attack_unit.hp - py_unit.unit_type.attack_damage

    @staticmethod
    def general_loop(script, py_unit, agent):
        """
        Since all scripts would use the same code to loop through enemy units, this single function instead
        handles the loops for all script.
        Afterwards based on what script called on this function, it will do what that specific script needs.
        """
        pos = py_unit.position
        attack_range = py_unit.unit_type.attack_range
        unit_list = agent.unit_collection.get_group(PLAYER_ENEMY, lambda u: u.unit_type.is_combat_unit)
        nearest_distance = 999999
        lowest_health = 999999
        strongest_attack = 0
        attack_unit = None

        for pyunit in unit_list:
            if pos.distance(pyunit.position) <= attack_range:

                if script == "attack_nearest":
                    if pos.distance(pyunit.position) < nearest_distance:
                        attack_unit = pyunit.unit
                        nearest_distance = pos.distance(pyunit.position)

                elif script == "attack_lowest":
                    if pyunit.hit_points < lowest_health:
                        attack_unit = pyunit.unit
                        lowest_health = pyunit.hit_points

                elif script == "kiting":
                    if pos.distance(pyunit.position) < attack_range \
                            and pos.distance(pyunit.position) < nearest_distance:
                        attack_unit = pyunit.unit
                        nearest_distance = pos.distance(pyunit.position)

                        if py_unit.unit.weapon_cooldown != 0:
                            kite_coords = AttackScripts.calculate_kite(py_unit, pyunit)
                            py_unit.move(kite_coords)
                            attack_unit = None

                elif script == "attack_strongest":
                    if pyunit.unit_type.attack_damage > strongest_attack:
                        attack_unit = pyunit.unit
                        strongest_attack = pyunit.unit_type.attack_damage

        if attack_unit:
            py_unit.unit.attack_unit(attack_unit)

    @staticmethod
    def calculate_kite(py_unit: PyUnit, pyunit: PyUnit):
        """Returns an appropriate position that a given unit should kite to."""
        pos = py_unit.position
        attack_range = py_unit.unit_type.attack_range
        delta_x = pos.x - pyunit.position.x
        delta_y = pos.y - pyunit.position.y
        # Calculate the distance between the points
        distance_to_enemy = pos.distance(pyunit.position)

        # Normalize the direction vector
        unit_delta_x = delta_x / distance_to_enemy
        unit_delta_y = delta_y / distance_to_enemy

        # Calculate the new position for the point
        new_x = pyunit.position.x + unit_delta_x * (attack_range + 1)
        new_y = pyunit.position.y + unit_delta_y * (attack_range + 1)
        return Point2D(new_x, new_y)

    # Function to calculate the distance between two points on the map
    Point2D.distance = lambda self, other: sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
