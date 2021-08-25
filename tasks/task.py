from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    from modules.py_unit import PyUnit
    from agents.basic_agent import BasicAgent

from library import UNIT_TYPEID, Point2D, Point2DI
from enum import Enum
import math


class Status(Enum):
    """
    A status code that a task should return form on_start, on_step, and on_fail.
    All fail statuses should be negative.
    """
    DONE = 1
    NOT_DONE = 0
    FAIL = -1
    FAIL_SUCCESSFUL = -2
    FAIL_FAILED = -3
    FAIL_CANT_AFFORD = -4
    FAIL_MISSING_PREREQUISITES = -5
    FAIL_DEAD = -6
    FAIL_TARGET_DEAD = -7
    FAIL_ALREADY_HAS_ADDON = -8

    def is_fail(self) -> bool:
        """Checks if a return is any form of Status.FAIL."""
        return self.value < 0


class Task:
    """
    A task is an action or series of actions a unit should preform.
    Prio describes the priority of the task. The lower the number, the higher the priority of the task.
    Candidates is a set of unit types that can preform the task.
    The target describes what the task is working on.
    """

    def __init__(self,
                 prio: int = 0,
                 candidates=None,
                 restart_on_fail=True,
                 agent: Optional[BasicAgent] = None):
        if candidates is None:
            candidates = set()
        self.prio: int = prio
        self.candidates: set[UNIT_TYPEID] = candidates
        self.restart_on_fail = restart_on_fail
        self.agent = agent
        self.target: Optional[Any] = None

    def __repr__(self):
        return f"<{type(self).__name__}: {str(self.target) + ', ' if self.target else ''}{self.prio}>"

    @property
    def target_position(self) -> Optional[Point2D]:
        """Returns the position of the task target, if any"""
        if isinstance(self.target, Point2D):
            return self.target
        elif isinstance(self.target, Point2DI):
            return Point2D(self.target.x, self.target.y)
        elif hasattr(self.target, "position"):
            return self.target.position
        return None

    def on_start(self, py_unit: PyUnit) -> Status:
        """
        Should be called when a unit starts the task, normally starts the task in the api.

        :param py_unit: The unit that called the method.
        :return: Status indicating the result of staring the task.
        """
        return Status.DONE

    def on_step(self, py_unit: PyUnit) -> Status:
        """
        Should be called to check if the task in progressing.

        :param py_unit: The unit that called the task.
        :return: Status indicating the result of performing the task.
        """
        return Status.DONE

    def on_fail(self, py_unit: PyUnit, status: Status) -> Status:
        """
        Called when a task fails, used to recover the task.

        :param py_unit: The unit that called the task.
        :param status: The status code from on_step.
        :return: Status indicating the result of recovering the task.
        """
        return status


class Idle(Task):
    """
    An idle task that a unit has when it does nothing.
    """

    def __init__(self, prio: int = math.inf):
        super().__init__(prio)
        self.restart_on_fail = False

    def on_step(self, py_unit: PyUnit) -> Status:
        """Keeps unit from doing nothing."""
        py_unit.stop()
        return Status.DONE
