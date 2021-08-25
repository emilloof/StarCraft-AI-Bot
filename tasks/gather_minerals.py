from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.py_unit import PyUnit
    from agents.basic_agent import BasicAgent

import random
from library import BaseLocation
from tasks.task import Task, Status


class GatherMinerals(Task):
    """Task for gathering minerals."""

    def __init__(self, base: BaseLocation, prio: int, agent: BasicAgent):
        super().__init__(prio=prio, candidates=agent.WORKER_TYPES)
        self.fail_count = 0
        self.target = base

    def on_start(self, py_unit: PyUnit) -> Status:
        """
        Start or restart the task.

        :return: Status.DONE if target are a mineral field. Otherwise Status.FAIL.
        """
        if self.target.minerals:
            py_unit.right_click(random.choice(self.target.minerals))
            self.fail_count = 0
            return Status.DONE
        else:
            return Status.FAIL

    def on_step(self, py_unit: PyUnit) -> Status:
        """
        Checks if the task is continuing.

        :return: Status.FAIL if target is not a mineral field or the unit have been idle for >10 ticks.
        Otherwise Status.NOT_DONE
        """
        if py_unit.is_idle:
            if self.target.minerals:
                py_unit.right_click(random.choice(self.target.minerals))
                self.fail_count += 1
                if self.fail_count > 10:
                    return Status.FAIL
                else:
                    return Status.NOT_DONE
            else:
                return Status.FAIL
        self.fail_count = 0
        return Status.NOT_DONE
