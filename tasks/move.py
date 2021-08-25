from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent

from library import Point2D
from modules.py_unit import PyUnit
from tasks.task import Task, Status


class Move(Task):
    """Task for moving a unit"""

    def __init__(self, pos: Point2D, prio: int, agent: BasicAgent):
        super().__init__(prio=prio, agent=agent)
        self.target = pos
        self.previous_pos: Optional[Point2D] = None
        self.fails: int = 0

    def on_start(self, py_unit: PyUnit) -> Status:
        """
        Start or restart the task.

        :return: Status.DONE if the task is started.
        """
        py_unit.move(self.target)
        self.previous_pos = py_unit.position
        return Status.DONE

    def on_step(self, py_unit: PyUnit) -> Status:
        """
        Checks if the task is continuing.

        :return: Status.DONE when unit is very close to the target (<1 tile). Status.NOT_DONE is
        unit is still on the move. Status.FAIL if unit is dead, idle have been stuck for >5 ticks.
        """
        if py_unit.is_idle:
            return Status.FAIL
        if py_unit.is_alive:
            # Are we at the selected target yet, or at least very, very close?
            if self.agent.maptools.get_ground_distance(py_unit.position, self.target) < 1:
                return Status.DONE
            # Are we stuck at the same position?
            elif py_unit.position == self.previous_pos:
                self.fails += 1
                # If we're stuck some time we count it as a fail.
                if self.fails == 5:
                    return Status.FAIL
            else:
                # We're still on the move.
                self.fails = 0
                self.previous_pos = py_unit.position
                return Status.NOT_DONE
        else:
            return Status.FAIL
