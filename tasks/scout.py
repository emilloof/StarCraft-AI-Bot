from __future__ import annotations
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from modules.py_unit import PyUnit
    from agents.basic_agent import BasicAgent

from library import UnitType, Point2D
from tasks.task import Task, Status
from queue import SimpleQueue
class Scout(Task):
    """Task for scouting a list of bases."""

    def __init__(self, scout_bases: SimpleQueue[Point2D], prio: int, agent: BasicAgent, **kwargs):
        super().__init__(prio=prio, candidates=agent.WORKER_TYPES, agent=agent, **kwargs)
        self.unit_type: Optional[UnitType] = None
        self.scout_bases: SimpleQueue[Point2D] = scout_bases
        self.scout_target: Optional[Point2D] = None
        self.fails: int = 0
        self.previous_pos: Optional[Point2D] = None
        
        #added. - hanlu520
        self.agent = agent
        
        
        # "Thus, what is of supreme importance in war is to attack the enemy's strategy", Sun Tzu, The Art of War.

    def on_start(self, py_unit: PyUnit) -> Status:
        """
        Start or restart the task.

        :return: Status.DONE if there is a list of targets and the task has been given to at suitable unit.
        Status.FAIL if unit not suitable.
        """
        # Preparing for different strategies depending on UNIT_TYPEID that's scouting.
        self.unit_type = py_unit.unit_type.unit_typeid

        #  If it has a target the task is restarted
        if self.target:

            py_unit.move(self.target)
            return Status.DONE

        # Sets first target, then removes it from list
        self.target = self.scout_bases.get()

        # From start only support for worker scouting.
        if self.unit_type in self.candidates:
            py_unit.move(self.target)
           
        # Features for other units could be added.
        else:
            return Status.FAIL
        return Status.DONE

    def on_step(self, py_unit: PyUnit) -> Status:
        """
        Checks if the task is continuing.

        :return: Status.DONE if unit is finished scouting. Status.NOT_DONE if it keeps scouting.
        Status.FAIL if unit is idle.
        """
        self.agent.latest_scout_unit = py_unit
        if not self.target:
            return Status.DONE

        if py_unit.is_idle:
            return Status.FAIL

        if not py_unit.is_alive:
            # If a scout dies and we return FAIL yet another one is automatically sent to (probably) the same destiny.
            # So even if the scouting fails, we claim DONE. Another scouting mission has to be ordered.
            return Status.DONE

        # Are we near the coordinate yet? Just close enough. < distance 5 arbitrarily chosen.
        if py_unit.position.square_distance(self.target) < 5 ** 2:
            return self.switch_target(py_unit)

        # Are we stuck?
        if py_unit.position == self.previous_pos:
            self.fails += 1
            if self.fails == 5:
                # Scout is really stuck. Trying to switch focus to next point of interest to scout.
                return self.switch_target(py_unit)
            return Status.NOT_DONE

        # We're still on the move.
        self.fails = 0
        self.previous_pos = py_unit.position

        return Status.NOT_DONE

    def switch_target(self, py_unit: PyUnit) -> Status:
        """Switch the task target to the next base in the queue"""
        if self.scout_bases.empty():
            # No more coordinates in list to scout.
            return Status.DONE
        else:
            # Switching target to next coordinates in list to scout.
            self.target = self.scout_bases.get()
            py_unit.move(self.target)

            return Status.NOT_DONE
