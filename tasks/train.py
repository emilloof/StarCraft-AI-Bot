from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent
    from modules.py_unit import PyUnit

from tasks.task import Task, Status
from library import UnitType, UPGRADE_ID, ABILITY_ID, Point2D, Point2DI
from modules import extra


class Train(Task):
    """Task for training a new unit."""

    def __init__(self, unit_type: UnitType, prio: int, agent: BasicAgent):
        producers = agent.tech_tree.get_data(unit_type).what_builds
        # TODO: Remove flying check if tech tree is updated to not include flying units in what builds
        super().__init__(prio=prio,
                         candidates=set([prod.unit_typeid for prod in producers if not prod.name.endswith("FLYING")]),
                         agent=agent)
        self.unit_type: UnitType = unit_type
        self.target = unit_type
        self.has_trained = False

    def on_start(self, py_unit: PyUnit) -> Status:
        """
        Start or restart the task.

        :return: Status.DONE if the task was started. Status.FAIL_CANT_AFFORD if we can't afford the task.
        Status.FAIL_MISSING_PREREQUISITES if we're missing prerequisites.
        """
        if not self.agent.can_afford(self.unit_type):
            return Status.FAIL_CANT_AFFORD

        if not extra.has_prerequisites(self.agent, self.unit_type):
            return Status.FAIL_MISSING_PREREQUISITES

        self.agent.pay(self.unit_type)
        py_unit.train(self.unit_type)
        return Status.DONE

    def on_step(self, py_unit: PyUnit) -> Status:
        """
        Checks if the task is continuing.

        :return: Status.DONE is done. Status.NOT_DONE if training. Otherwise Status.FAIL.
        """
        if py_unit.is_training:
            self.has_trained = True
            return Status.NOT_DONE

        if self.has_trained:
            return Status.DONE

        return Status.FAIL


class BuildAddon(Train):
    """Task for building an addon onto a unit."""

    def __init__(self, unit_type: UnitType, prio: int, agent: BasicAgent):
        super().__init__(unit_type, prio, agent)
        self.moving = False
        self.move_to: Optional[Point2DI] = None
        self.fails = 0
        self.previous_pos: Optional[Point2D] = None

    def on_start(self, py_unit: PyUnit) -> Status:
        """
        Start or restart the task.

        :return: Status.DONE if the task was started. Status.FAIL_ALREADY_HAS_ADDON if building already has any.
        addon.
        """
        if extra.get_addon(self.agent, py_unit) is not None:
            return Status.FAIL_ALREADY_HAS_ADDON

        if not self.agent.py_building_placer.can_build_addon(py_unit):
            # Move to a different location where the addon can be built (hopefully)
            self._start_move(py_unit)
            return Status.DONE

        return super().on_start(py_unit)

    def on_step(self, py_unit: PyUnit) -> Status:
        """
        Checks if the task is continuing.

        :return: Status.DONE is done. Status.NOT_DONE if training. Otherwise Status.FAIL.
        """
        if self.moving:
            if self.move_to is None:
                return Status.FAIL

            if py_unit.position == self.previous_pos:
                self.fails += 1
            else:
                self.fails = 0
            if self.fails >= 10:
                # Unit is stuck, find new position
                self.move_to = self.agent.py_building_placer.get_new_addon_pos(py_unit)
                self.fails = 0
            self.previous_pos = py_unit.position

            py_unit.ability(ABILITY_ID.LAND, self.move_to)
            if not (py_unit.is_flying or py_unit.unit_type.name.endswith("FLYING")):
                # Unit has landed, try to build addon again
                self.move_to = None
                self.moving = False
                restart = self.on_start(py_unit)
                if restart.is_fail():
                    return Status.FAIL
            return Status.NOT_DONE

        super_status = super().on_step(py_unit)
        if super_status.is_fail():
            # We tried to build an addon but we could not
            self._start_move(py_unit)
            return Status.NOT_DONE

        return super_status

    def on_fail(self, py_unit: PyUnit, status: Status) -> Status:
        """Handles task fail."""
        # In case we are still flying when we fail, land at current position
        py_unit.ability(ABILITY_ID.LAND, py_unit.position)
        return Status.FAIL_SUCCESSFUL

    def _start_move(self, py_unit: PyUnit) -> None:
        """Lift py_unit and enter moving state."""
        self.move_to = self.agent.py_building_placer.get_new_addon_pos(self.unit_type, py_unit)
        py_unit.unit.ability(ABILITY_ID.LIFT)
        self.moving = True
        self.previous_pos = py_unit.position


class Morph(Train):
    """Task for morphing into a new unit type, e.g. Command Center -> Orbital Command."""

    def __init__(self, unit_type: UnitType, prio: int, agent: BasicAgent):
        super().__init__(unit_type, prio, agent)

    def on_start(self, py_unit: PyUnit) -> Status:
        """
        Start or restart the task.

        :return: Status.DONE if the task was started. Status.FAIL_CANT_AFFORD if we can't afford the task.
        Status.FAIL_MISSING_PREREQUISITES if we're missing prerequisites. Status.FAIL if unit's already training.
        """
        if not self.agent.can_afford(self.unit_type):
            return Status.FAIL_CANT_AFFORD

        if not extra.has_prerequisites(self.agent, self.unit_type):
            return Status.FAIL_MISSING_PREREQUISITES

        if py_unit.is_training:
            return Status.FAIL

        self.agent.pay(self.unit_type)
        py_unit.morph(self.unit_type)
        return Status.DONE


class Research(Train):
    """Task for researching an upgrade."""

    def __init__(self, unit_type: UPGRADE_ID, prio: int, agent: BasicAgent):
        if isinstance(unit_type, UPGRADE_ID) and unit_type == UPGRADE_ID.COMBATSHIELD:
            unit_type = UPGRADE_ID.SHIELDWALL

        super().__init__(unit_type, prio, agent)

    def on_start(self, py_unit: PyUnit) -> Status:
        """
        Start or restart the task.

        :return: Status.DONE if the task was started. Status.FAIL_CANT_AFFORD if we can't afford the task.
        Status.FAIL_MISSING_PREREQUISITES if we're missing prerequisites.
        """
        if not self.agent.can_afford(self.unit_type):
            return Status.FAIL_CANT_AFFORD

        if not extra.has_prerequisites(self.agent, self.unit_type):
            return Status.FAIL_MISSING_PREREQUISITES

        if py_unit.is_training:
            return Status.FAIL

        self.agent.pay(self.unit_type)
        py_unit.research(self.unit_type)
        return Status.DONE
