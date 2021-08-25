from __future__ import annotations
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent
from library import UnitType, Point2DI, Point2D, PLAYER_SELF
from modules.py_unit import PyUnit
from typing import Optional
from tasks import build


class PyBuildingPlacer:
    """Class of tools that help placement of buildings"""
    def __init__(self, agent: BasicAgent):
        self.agent = agent

    def find_position(self, type_to_build: UnitType) -> Point2DI:
        """
        Finds a postion to build a building of the type_to_build
        :param type_to_build:
        :return:
        """
        # If it is a refinery it needs to be build on top of a geyser
        if type_to_build.is_refinery:
            pos = self.find_refinery_position()
        # If a new Town hall is to be built, we want it at the next expansion position
        elif type_to_build.is_resource_depot:
            pos = self.agent.base_location_manager.get_next_expansion(PLAYER_SELF).depot_position
        else:
            pos = self.agent.building_placer.get_build_location_near(
                self.agent.base_location_manager.get_player_starting_base_location(PLAYER_SELF).depot_position,
                type_to_build)
        return pos

    def find_refinery_position(self) -> Optional[PyUnit]:
        """
        Goes through each occupied base and checks if there are refineries at each location. If it finds a free spot it
        returns its location, None otherwise.
        """

        refineries = [ref.tile_position for ref in
                      self.agent.unit_collection.get_group(PLAYER_SELF, lambda u: u.unit_type.is_refinery)]
        upcoming = [t.pos.tile_position for t in
                    self.agent.task_manager.current_tasks.get_tasks(build.Build, None).union(
                        self.agent.task_manager.task_queue.get_tasks(build.Build, None)) if
                    t.building_type.is_refinery and t.pos]
        for base_location in self.agent.base_location_manager.get_occupied_base_locations(PLAYER_SELF):
            for geyser in base_location.geysers:
                if geyser.tile_position not in refineries + upcoming:
                    return self.agent.unit_collection.get_py_unit(geyser.id)
        return None

    def can_build_addon(self, candidate: PyUnit) -> bool:
        """
        Checks if an addon can be built on unit "candidate".

        Notes: If the addon would be built in a ramp (which it cannot), this function still returns True.

        :return: Boolean indicating if addon can be built
        """
        addon_pos = candidate.tile_position + Point2DI(3, 0)
        res = self.agent.building_placer.can_build_here_with_size(addon_pos.x, addon_pos.y, 1, 1)
        return res

    def check_and_fix_building_place(self,
                                     pos: Union[Point2DI, PyUnit],
                                     building_type: UnitType
                                     ) -> tuple[bool, Union[Point2DI, PyUnit]]:
        """
        Checks if the position is still buildable if it is not a new position is generated if possible
        :param pos:
        :param building_type:
        :return: If a legal position was crated or not, and the position
        """
        if isinstance(pos, Point2DI):
            if self.agent.building_placer.can_build_here(pos.x, pos.y, building_type):
                # pos is still a valid build location, nothing to fix
                return True, pos

            if building_type.is_resource_depot:
                # Recalculate next expansion position
                pos = self.agent.base_location_manager.get_next_expansion(PLAYER_SELF).depot_position
                return True, pos

            # Find new build location near old build location
            pos = self.agent.building_placer.get_build_location_near(pos, building_type)
            if pos == Point2DI(0, 0):
                # We could not find a new build location, try to find one near one of our bases
                bases = self.agent.base_location_manager.get_occupied_base_locations(PLAYER_SELF)
                if not bases:
                    return False, pos
                for base in bases:
                    pos = self.agent.building_placer.get_build_location_near(base.depot_position, building_type)
                    if pos != Point2DI(0, 0):
                        return True, pos
                # No base had a valid build location near it
                return False, pos
        elif isinstance(pos, PyUnit):
            # pos is a Vespene Geyser
            pos = self.find_refinery_position()
            if not pos:
                return False, pos

        return True, pos

    def get_new_addon_pos(self, unit_type: UnitType, py_unit: PyUnit) -> Optional[Point2D]:
        """
        Tries to find a new position where there is space for an addon to be built.
        Searches for positions near "py_unit" first, and then around own bases.

        :return: New position where addon can be build, if any
        """
        pos = py_unit.agent.building_placer.get_build_location_near(py_unit.tile_position,
                                                                    unit_type,
                                                                    distance_to_building=0)
        if pos == Point2DI(0, 0):
            # We could not find a new location, try to find one near one of our bases
            bases = self.agent.base_location_manager.get_occupied_base_locations(PLAYER_SELF)
            if not bases:
                return None
            for base in bases:
                pos = self.agent.building_placer.get_build_location_near(base.depot_position,
                                                                         unit_type,
                                                                         distance_to_building=0)
                if pos != Point2DI(0, 0):
                    return Point2D(pos)
            # No base had a valid build location near it
            return None

        return Point2D(pos)
