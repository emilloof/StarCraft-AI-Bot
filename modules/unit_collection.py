from __future__ import annotations
from typing import TYPE_CHECKING, Union, Any

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent

from library import PLAYER_SELF, PLAYER_ENEMY, PLAYER_NEUTRAL, UNIT_TYPEID, Unit
from modules.py_unit import PyUnit
from tasks.task import Task


class UnitCollection:
    """A class to handle the connection between a library Unit and MyUnit, and handle unit groups."""

    def __init__(self, agent: BasicAgent):
        self.agent: BasicAgent = agent
        self.py_units: dict[int, PyUnit] = {}
        self.groups: dict[Union[any], set[PyUnit]] = {}
        self.create_group(PLAYER_SELF)
        self.create_group(PLAYER_ENEMY)
        self.create_group(PLAYER_NEUTRAL)
        self.needs_vision_on: list[PyUnit] = []
        self.new_units_this_step: list[PyUnit] = []

    def __iter__(self):
        for py_unit in self.py_units.values():
            yield py_unit

    def __contains__(self, item):
        return item in self.py_units

    def get_group(self, *keys: Any) -> set[PyUnit]:
        """
        Gives the PyUnits that match all keys except for unit_typeids where the unit only needs to match one unit type.
        If multiple unit_types is given the preforms is better if it is given as a lambda function.

        :param keys: A number of identifying keys: group keys, current task type, lambda function, or unit_typeids.
        For unit type ids, the unit only needs to have one of the given types.
        :return: A set of PyUnits that match the keys.
        """
        return_set = set(self.py_units.values())
        unit_type_set: set = set()
        unit_typeid_used = False
        for key in keys:
            if isinstance(key, UNIT_TYPEID):
                new_set = {py_unit for py_unit in return_set if py_unit.unit_type.unit_typeid == key}
                unit_type_set = unit_type_set.union(new_set)
                unit_typeid_used = True
            else:
                if key in self.groups:
                    return_set = return_set.intersection(self.groups[key])
                elif isinstance(key, type) and issubclass(key, Task):
                    return_set = {py_unit for py_unit in return_set if isinstance(py_unit.task, key)}
                elif callable(key):
                    return_set = {py_unit for py_unit in return_set if key(py_unit)}
                else:
                    return_set = set()

        if unit_typeid_used:
            return_set = return_set.intersection(unit_type_set)

        return return_set

    def get_py_unit(self, unit_id: int) -> PyUnit:
        """Gets a unit by id from the collection."""
        return self.py_units[unit_id]

    def on_step(self) -> None:
        """Updates the unit collection to reflect the current state of the game."""
        # If a neutral or enemy unit leaves the vision it will get a new id the next time it is visible.
        self.needs_vision_on = list(self.get_group(PLAYER_NEUTRAL).union(self.get_group(PLAYER_ENEMY)))

        self.new_units_this_step = []
        for unit in self.agent.get_all_units():
            # The building indication has id 0.
            if unit.id != 0:
                is_new_unit = self.add_or_update(unit)
                if is_new_unit:
                    self.new_units_this_step.append(self.get_py_unit(unit.id))

        # All units that have left the vision are removed
        for py_unit in self.needs_vision_on:
            self.remove_from_all_groups(py_unit)
        self.remove(self.needs_vision_on)
        self.needs_vision_on = []

    def add_or_update(self, unit: Unit) -> bool:
        """
        Adds the unit to the collection if it is new, updates it otherwise.
        It also adds the unit to the group for the player, and if it is a refinery it is added to a base group.

        :param unit: A library unit to add or update.
        :return: Boolean indicating if the unit was new (i.e. added, not updated).
        """
        if unit.id not in self.py_units:
            # New unit, add it
            py_unit = PyUnit(unit, self.agent)
            self.py_units[unit.id] = py_unit
            self.add_to_group(unit.player, py_unit)

            # The refinery is added to the group of its closest base, so it can easily be found when tasks are generated
            if unit.player == PLAYER_SELF and unit.unit_type.is_refinery:
                correct_base = min(self.agent.base_location_manager.get_occupied_base_locations(PLAYER_SELF),
                                   key=lambda b: b.position.square_distance(unit.position),
                                   default=None)
                if correct_base is not None:
                    self.add_to_group(correct_base, py_unit)
            return True
        else:
            # Already saved unit, update it
            py_unit = self.py_units[unit.id]
            py_unit.unit = unit
            if unit.player != PLAYER_SELF:
                self.needs_vision_on.remove(py_unit)
            return False

    def remove(self, py_units: list[PyUnit]) -> None:
        """All unit in the list is removed from the collection."""
        for py_unit in py_units:
            self.py_units.pop(py_unit.id)

    def add_to_group(self, key: Any, py_unit: PyUnit) -> None:
        """The unit is added to the group with the key."""
        if key not in self.groups:
            self.create_group(key)
        self.groups[key].add(py_unit)
        py_unit.add_group(key)

    def create_group(self, key: Any) -> None:
        """Creates a new empty group."""
        self.groups[key] = set()

    def remove_group(self, key: Any) -> None:
        """Removes a group."""
        for py_unit in self.groups[key]:
            py_unit.remove_group(key)
        self.groups.pop(key)

    def remove_from_all_groups(self, py_unit: PyUnit) -> None:
        """Removes the unit from all groups, should only be used when the unit is removed from the unit collection."""
        for key in py_unit.groups:
            if key in self.groups:
                self.groups[key].remove(py_unit)
        py_unit.groups.clear()

    def remove_from_group(self, key: Any, py_unit: PyUnit) -> None:
        """Remove a unit from a group."""
        if key in self.groups:
            self.groups[key].remove(py_unit)
            py_unit.remove_group(key)

    def remove_dead_units(self) -> None:
        """Removes dead units from the unit collection."""
        dead_units = []
        for py_unit in self.py_units.values():
            if not py_unit.is_alive:
                py_unit.on_death()
                dead_units.append(py_unit)
                self.remove_from_all_groups(py_unit)
        if dead_units:
            self.remove(dead_units)
