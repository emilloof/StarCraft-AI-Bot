from __future__ import annotations
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from tasks.task import Task
    from library import Unit
    from agents.basic_agent import BasicAgent

from tasks.task import Idle, Status


class PyUnit:
    """
    Class representing a StarCraft II unit.
    This class contains a library Unit, and extra information.
    """

    def __init__(self, unit: Unit, agent: BasicAgent):
        self.unit: Unit = unit
        self.task: Task = Idle()
        self.groups = set()
        self.agent: BasicAgent = agent
        self.max_weapon_cooldown = PyUnit.unit_cooldowns.get(unit.unit_type.name)
        self._last_weapon_cooldown = 0
        self.hp = unit.hit_points
        self.kite = False

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

    def on_step(self) -> Status:
        """
        Perform the unit's actions for this step.

        :return: Status indicating the result of performing actions.
        """
        if self.is_alive:
            status = self.task.on_step(self)
            if status.is_fail():
                status = self.task.on_fail(self, status)
        else:
            status = Status.FAIL_DEAD
        return status

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
        "PROTOSS_HIGHTEMPLAR": 0.001,  # High Templar's Feedback has no cooldown
        "TERRAN_REAPER": 1.5,
        "TERRAN_BATTLECRUISER": 0.23,
        "ZERG_MUTALISK": 0.56,
        "ZERG_ULTRALISK": 0.497,
        "TERRAN_BANSHEE": 0.8
    }