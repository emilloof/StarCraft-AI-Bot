from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from modules.py_unit import PyUnit
    from agents.basic_agent import BasicAgent

from library import Point2D
from tasks.task import Task, Status


class Attack(Task):
    """Task for attacking a position."""

    def __init__(self, pos: Point2D, prio: int, agent: BasicAgent):
        super().__init__(prio=prio, candidates=agent.COMBAT_TYPES)
        self.target = pos
        self.previous_pos: Optional[Point2D] = None
        self.fails: int = 0

    def on_start(self, py_unit: PyUnit) -> Status:
        """
        Start or restart the task.

        :return: Status.DONE if the task was started, Status.FAIL if task target is not Point2D.
        """
        # Target is a coordinate
        if isinstance(self.target, Point2D):
            py_unit.attack_move(self.target)
        else:
            return Status.FAIL
        return Status.DONE

    def on_step(self, py_unit: PyUnit) -> Status:
        """
        Checks if the task is continuing.

        :return: Status.DONE if the unit is idle. Status.FAIL if the unit is dead. Otherwise returns Status.NOT_DONE.
        """
        if py_unit.is_idle:
            return Status.DONE

        if not py_unit.is_alive:
            # Unit is dead
            return Status.FAIL

        return Status.NOT_DONE
