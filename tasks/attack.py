from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from tasks.attack_scripts import AttackScripts
from tasks.attack_decider import *

if TYPE_CHECKING:
    from modules.py_unit import PyUnit
    from agents.basic_agent import BasicAgent

from library import Point2D
from tasks.task import Task, Status


class Attack(Task):
    """Task for attacking a position."""

    def __init__(self, pos: Point2D, prio: int, agent: BasicAgent):
        super().__init__(prio=prio, candidates=agent.COMBAT_TYPES, agent=agent)
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
            py_unit.move(self.target)
        else:
            return Status.FAIL
        return Status.DONE

    def on_step(self, py_unit: PyUnit) -> Status:
        """
        Checks if the task is continuing.

        :return: Status.DONE if the unit is idle. Status.FAIL if the unit is dead. Otherwise returns Status.NOT_DONE.
        """
        if py_unit.is_idle:
            if py_unit.kite:
                py_unit.kite = False
                py_unit.move(self.target)
            else:
                return Status.DONE

        if not py_unit.is_alive:
            # Unit is dead
            return Status.FAIL

        state = Situation(self.agent, py_unit, PLAYER_SELF)
        alpha_beta_search(state, 3, True)
        AttackScripts.general_loop(state.script, py_unit, self.agent)

        return Status.NOT_DONE
