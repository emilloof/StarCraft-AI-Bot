from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from modules.py_unit import PyUnit
    from agents.basic_agent import BasicAgent

from tasks.task import Task, Status


class GatherGas(Task):
    """Task for gathering gas."""

    def __init__(self, refinery: PyUnit, prio: int, agent: BasicAgent):
        super().__init__(prio=prio, candidates=agent.WORKER_TYPES)
        self.target: Optional[PyUnit] = refinery

    def on_start(self, py_unit: PyUnit) -> Status:
        """
        Start or restart the task.

        :return: Status.DONE when the task was started.
        """
        py_unit.right_click(self.target.unit)
        return Status.DONE

    def on_step(self, py_unit: PyUnit) -> Status:
        """
        Checks if the task is continuing.

        :return: Status.FAIL if the unit is idle, Status.NOT_DONE if the unit is alive and there are gas left
        in the refinery. Returns Status.DONE if unit is dead or the refinery is out of gas.
        """
        if py_unit.is_idle:
            return Status.FAIL
        # It there still a refinery and does it have gas left in the geyser?
        if self.target.is_alive and self.target.gas_left_in_refinery:
            return Status.NOT_DONE
        else:
            return Status.DONE
