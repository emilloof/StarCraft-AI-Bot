from __future__ import annotations
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent

from library import UnitType, Point2DI, Unit, PLAYER_SELF
from tasks.task import Task, Status
from modules.py_unit import PyUnit
from modules import extra


class Build(Task):
    """A task for building buildings"""

    def __init__(self, building_type: UnitType, pos: Union[Point2DI, PyUnit], prio: int, agent: BasicAgent):
        producers = agent.tech_tree.get_data(building_type).what_builds
        super().__init__(prio=prio, candidates=set([prod.unit_typeid for prod in producers]), agent=agent)
        self.building_type: UnitType = building_type
        self.pos: Union[Point2DI, Unit] = pos
        self.fail_counter: int = 0

    def __repr__(self):
        return f"<Build: {self.target if self.target else self.building_type}, {self.prio}>"

    def on_start(self, py_unit: PyUnit) -> Status:
        """
        Start or restart the task.

        :return: Status.DONE if the task was started, Status.FAIL_CANT_AFFORD if the agent cant afford the building,
        Status.FAIL_MISSING_PREREQUISITES if required buildings or upgrades is missing, Status.FAIL if the pos is
        something else
        """
        #  The task is restarted and the unit just needs to continue
        if self.target and self.target.is_alive:
            py_unit.right_click(self.target.unit)
            return Status.DONE

        if not self.agent.can_afford(self.building_type):
            return Status.FAIL_CANT_AFFORD

        if not extra.has_prerequisites(self.agent, self.building_type):
            return Status.FAIL_MISSING_PREREQUISITES

        if isinstance(self.pos, Point2DI):
            self.agent.pay(self.building_type)
            py_unit.build(self.building_type, self.pos)
        elif isinstance(self.pos, PyUnit):
            self.agent.pay(self.building_type)
            if self.pos.unit.id not in self.agent.unit_collection:
                self.pos = self.agent.unit_collection.get_group(
                    lambda u: u.unit_type.is_geyser and u.position == self.pos.position).pop()
            py_unit.build_target(self.building_type, self.pos.unit)
        else:
            return Status.FAIL

        self.fail_counter: int = 0
        return Status.DONE

    def on_step(self, py_unit: PyUnit) -> Status:
        """
        Checks if the building is progressing.

        :return: Status.DONE if the building is done, Status.FAIL_TARGET_DEAD if the building that is being constructed
        is destroyed, return Status.FAIL if the unit has the wrong target or is idle, Status.NOT_DONE if the task is
        not done
        """
        # The building is being built.
        if self.target and self.target.build_percentage > 0:
            if self.target.is_completed:
                return Status.DONE
            if not self.target.is_alive:
                self.target = None
                return Status.FAIL_TARGET_DEAD
        else:
            # Timeout
            if self.fail_counter > 100:  # 100 is arbitrarily chosen (corresponds to 1000 ticks in game).
                return Status.FAIL

            # The instance of the building the unit is constructing is set as task target.
            if self.fail_counter > 10 and py_unit.has_target:
                # The units target should be of the correct type, when building a refinery the target will be the
                # geyser when the unit moves to the geyser.
                if self.building_type.is_refinery:
                    if not py_unit.target.unit_type.is_geyser and py_unit.target.unit_type != self.building_type:
                        return Status.FAIL
                else:
                    if py_unit.target.unit_type != self.building_type:
                        return Status.FAIL
            if py_unit.is_constructing(self.building_type):
                buildings = self.agent.unit_collection.get_group(self.building_type.unit_typeid, PLAYER_SELF,
                                                                 lambda u: not u.is_completed)
                if buildings:
                    pos = self.pos
                    if isinstance(pos, PyUnit):
                        pos = pos.tile_position
                    target = [my_u for my_u in buildings if pos == my_u.tile_position]
                    if target and target[0].id != 0:
                        self.target = target[0]

            self.fail_counter += 1
        if py_unit.is_idle:
            return Status.FAIL
        return Status.NOT_DONE

    def on_fail(self, py_unit: PyUnit, status: Status) -> Status:
        """
        Tries to recover from the fail.

        :param py_unit:
        :param status:
        :return:
        """
        if status == Status.FAIL_DEAD or status == Status.FAIL_TARGET_DEAD:
            return status

        fixed, pos = self.agent.py_building_placer.check_and_fix_building_place(self.pos, self.building_type)
        if fixed:
            self.pos = pos
            return Status.FAIL_SUCCESSFUL
        else:
            return Status.FAIL_FAILED
