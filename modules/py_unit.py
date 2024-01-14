from __future__ import annotations
from typing import TYPE_CHECKING, Any
from math import cos, sin, pi

if TYPE_CHECKING:
    from tasks.task import Task
    from library import Unit
    from agents.basic_agent import BasicAgent

from library import Point2D, PLAYER_ENEMY
from .extra import get_closest, get_friendly_in_radius
from functools import cached_property, cache
from tasks.task import Idle, Status
from modules.potential_flow.vector import Vector
from modules.cache_manager import add_expire_instance, add_expire_function, update_my_functions
from config import USE_PFSCOUT


class PyUnit:
    """
    Class representing a StarCraft II unit.
    This class contains a library Unit, and extra information.
    """

    def __init__(self, unit: Unit, agent: BasicAgent, last_seen: int = None, fade_time: int = None):
        self.unit: Unit = unit
        self.task: Task = Idle()
        self.groups = set()
        self.agent: BasicAgent = agent
        self.max_weapon_cooldown = PyUnit.unit_cooldowns.get(unit.unit_type.name)
        self._last_weapon_cooldown = 0
        self.hp = unit.hit_points
        self.kite = False
        
        #Hannes
        self.next = 0

        self.p_value = unit.unit_type.attack_range
        # time to keep the unit in knowledge base before determined old knowledge
        self.last_seen = last_seen
        self.fade_time = fade_time
        add_expire_instance(self.agent, self)
        add_expire_function(self.agent, self, self.get_target, 48)
        # TODO: Add previous known position, in case Unit.position does not work

    def __repr__(self):
        return f"<PyUnit: {self.unit_type.name}, {self.id}>"

    def __getattr__(self, item):
        """
        Gets an attribute.
        If attribute is not in MyUnit, get it from self.unit
        """
        if item not in self.__dict__.keys():
            return getattr(self.unit, item)
        return object.__getattribute__(self, item)

    @cached_property
    def is_enemy(self) -> bool:
        """Returns if unit is an enemy"""
        return PLAYER_ENEMY in self.groups

    @cache
    def get_target(self):
        return self.target

    @property
    def target(self) -> Unit:
        """Returns the unit's target"""
        if not self.is_enemy:
            return self.unit.target if self.has_target else None
        # else (self.unit is an enemy)
        # TODO: check if this (enemy unit) is doing an action/ability where it could even have the scout as target
        if friendly_in_range := get_friendly_in_radius(self.agent, self.unit.position,
                                                       self.unit.unit_type.sight_range):
            # Filter units that are within a certain angle of the enemy unit's facing direction
            friendly_facing = self.get_units_facing_unit(friendly_in_range)

            if friendly_facing:
                return get_closest(friendly_facing, self.unit.position, lambda u: u.position)

    @cached_property
    def can_attack(self) -> bool:
        """Returns if unit_type can attack"""
        return self.unit.unit_type.attack_damage > 0

    def on_step(self) -> Status:
        """
        Perform the unit's actions for this step.

        :return: Status indicating the result of performing actions.
        """
        if self.is_alive:
            status = self.task.on_step(self)
            if status.is_fail():
                status = self.task.on_fail(self, status)
            if USE_PFSCOUT:
                update_my_functions(self.agent, self)
        else:
            status = Status.FAIL_DEAD
        return status

    def get_units_facing_unit(self, units: set[PyUnit]) -> set[PyUnit]:
        """Returns units that are within a certain angle of the unit's facing direction"""
        return [u for u in units if abs(self.position.angle_to(u.position) - self.facing) < pi / 4]

    def on_death(self) -> None:
        """Handle unit death"""
        pass

    def give_task(self, task: Task) -> Status:
        """Gives a new task to the unit"""

        status = task.on_start(self)
        if not status.is_fail():
            self.task = task
        return status

    def add_group(self, key: Any) -> None:
        """Adds a group to unit's groups"""
        self.groups.add(key)

    def remove_group(self, key: Any) -> None:
        """Removes a group from unit's groups"""
        self.groups.remove(key)

    def get_hp(self):
        unit_hp = self.unit.hit_points
        return unit_hp

    def clone(self):
        return PyUnit(self.unit, self.agent)

    #List of all cooldown for each units. Used in init for each pyunit.
    unit_cooldowns = {
        'TERRAN_MARINE': 0.86,
        "TERRAN_SIEGETANK": 3.04,
        "PROTOSS_ZEALOT": 0.86,
        "ZERG_ZERGLING": 0.696,
        "PROTOSS_STALKER": 1.44,
        "ZERG_ROACH": 2.2,
        "TERRAN_HELLION": 1.43,
        "TERRAN_HELLBAT": 1.43,
        "PROTOSS_IMMORTAL": 1.45,
        "PROTOSS_VOIDRAY": 0.36,
        "PROTOSS_COLOSSUS": 2.21,
        "PROTOSS_HIGHTEMPLAR": 0.001,    # High Templar's Feedback has no cooldown
        "TERRAN_REAPER": 1.5,
        "TERRAN_BATTLECRUISER": 0.23,
        "ZERG_MUTALISK": 0.56,
        "ZERG_ULTRALISK": 0.497,
        "TERRAN_BANSHEE": 0.8
    }
