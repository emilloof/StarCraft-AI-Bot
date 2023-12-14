from __future__ import annotations
from typing import TYPE_CHECKING

from config import TIME_KEEP_ENEMY, TIME_KEEP_ENEMY_BUILDING, DEBUG_SCOUT
from modules.extra import get_closest, get_enemy_start_pos

from modules.potential_flow.regions import Region
from modules.potential_flow.potentials import calculate_pval
from modules.potential_flow.vector import Vector
from tasks.task import Status
from tasks.scout import Scout
from modules.py_unit import PyUnit

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent

from library import Point2D, Point2DI, Color
from queue import SimpleQueue

show_object_r = True
show_unit_p = True
show_region_p = True
show_border_p = True
show_all_p = False

SECOND_IN_FRAMES = 16


class PFscout(Scout):

    def __init__(self, scout_bases: SimpleQueue[Point2D], prio: int, agent: BasicAgent):
        super().__init__(None, prio, agent, is_high_freq=True)
        # super().__init__(scout_bases, prio, agent)
        self.target_region: Region = None
        self.go = 1  # 1: proceed forward, -1: reverse direction

        self.CENTER_VORTEX = 19
        self.CENTER_SOURCE_SINK = 3
        self.DISTANCE_TO_SWITCH_SOURCE_SINK = 4
        self.DISTANCE_TO_ACTIVE_BORDER_FLOW = 3
        self.BORDER_VORTEX = -16
        self.BORDER_SOURCE = 9
        self.BUILDING_OBSTACLE = 5
        self.ENEMY_NEEDLE = 9

        self.enemies = set()
        self.attract_points: set[Point2D] = set()

        self.frame_since_switch = 0
        self.switch_region = False
        self.changed_region = False

        self.use_border = True

        if DEBUG_SCOUT:
            self.region_potentials: list[Vector] = []
            self.border_potentials = []
            self.all_potentials = []
            self.obstacles_debug = set()
            self.unit_potentials = []

    def on_start(self, py_unit: PyUnit) -> Status:
        """
        Start or restart the task.

        :return: Status.DONE if there is a list of targets and the task has been given to at suitable unit. # noqa
        Status.FAIL if unit not suitable.
        """

        if py_unit.unit_type.unit_typeid in self.candidates:
            return Status.DONE
        print("FAIL")
        return Status.FAIL

    def on_step(self, py_unit: PyUnit) -> Status:
        """
        Checks if the task is continuing.

        :return: Status.DONE if unit is finished scouting. Status.NOT_DONE if it keeps scouting.
        Status.FAIL if unit is idle.
        """
        self.scout_enemy_opening(py_unit)

        self.fade_enemies()    # should (according *) be at top of do_pf()

        return Status.NOT_DONE

    def do_pf(self, py_unit):
        # Control scout's movement using potential flow
        self.move(py_unit)

        if DEBUG_SCOUT:
            self.debug(py_unit)

    def debug(self, py_unit: PyUnit):
        if show_object_r:
            if self.target_region:
                cur_center = self.target_region.center
                self.agent.map_tools.draw_circle(cur_center, 3, Color.RED)
                self.agent.map_tools.draw_circle(cur_center, self.DISTANCE_TO_SWITCH_SOURCE_SINK,
                                                 Color.TEAL)
            for obj in self.obstacles_debug:
                self.agent.map_tools.draw_circle(obj[0].position, obj[1], Color.TEAL)
        scout_pos = py_unit.position
        if show_unit_p:
            for up in self.unit_potentials:
                self.agent.map_tools.draw_line(scout_pos, up + scout_pos, Color.RED)
                self.agent.map_tools.draw_circle(up + scout_pos, 2, Color.RED)

        if show_region_p:
            for rp in self.region_potentials:
                self.agent.map_tools.draw_line(scout_pos, rp + scout_pos, Color.YELLOW)
                self.agent.map_tools.draw_circle(rp + scout_pos, 2, Color.YELLOW)

        if show_border_p:
            for bp in self.border_potentials:
                self.agent.map_tools.draw_line(
                    scout_pos, bp + scout_pos, Color(255, 165, 0))  # orange
                self.agent.map_tools.draw_circle(bp + scout_pos, 2, Color(255, 165, 0))
                self.agent.map_tools.draw_text(bp + scout_pos, "b", Color.WHITE)

        if show_all_p:
            for p in self.all_potentials:
                self.agent.map_tools.draw_line(scout_pos, p + scout_pos, Color.TEAL)
                self.agent.map_tools.draw_circle(p + scout_pos, 2, Color.TEAL)

    def near_reach_pos(self, pos1, pos2, dist=0.25):
        return pos1.distance(pos2) < dist

    def move(self, py_unit: PyUnit):
        # Code for controlling scout's movement using potential flow

        scout_pos = py_unit.unit.position

        if not (self.agent.current_frame % 1 == 0
                or self.near_reach_pos(scout_pos, self.scout_target) or
                (self.near_reach_pos(scout_pos, py_unit.target.position, 1))):
            return  # do nothing

        this_target = py_unit.position    # self.scout_target

        ###

        # DUNNO IF NEEDED
        # self.target_region = self.target_region or get_region(self.agent, py_unit.tile_position).

        # reverse all flows values if needed
        should_reverse = self.go
        self.reverse_flows(should_reverse)
        speed = calculate_pval(self, py_unit)
        # reverse back
        self.reverse_flows(should_reverse)

        self.scout_target = scout_pos + speed

        ratio = 1 / speed.length()
        seg = speed * ratio
        this_target = (seg * 3) + this_target
        while not self.agent.map_tools.is_walkable(Point2DI(this_target)):
            this_target = seg + this_target

            if self.agent.map_tools.is_valid_position(this_target):
                break

        if DEBUG_SCOUT:
            self.agent.map_tools.draw_tile(Point2DI(this_target))
            self.agent.map_tools.draw_text(py_unit.position, "scout", Color.WHITE)

        py_unit.move(this_target)

    def register_enemy_positions(self, enemies: set[PyUnit]):
        for enemy in enemies:
            if enemy in self.enemies:
                enemy.last_seen = self.agent.current_frame
            else:
                enemy.fade_time = (TIME_KEEP_ENEMY_BUILDING if enemy.unit_type.is_building
                                   else TIME_KEEP_ENEMY)
                self.enemies.add(enemy)

    def get_enemies(self):
        return self.enemies

    def add_attract_point(self, attract_point):
        self.attract_points.add(attract_point)

    def set_scout_target(self, scout_target):
        self.scout_target = scout_target

    def fade_enemies(self):
        enemies_to_remove = {
            enemy
            for enemy in self.enemies
            if self.agent.current_frame - enemy.last_seen > enemy.fade_time
        }
        self.enemies -= enemies_to_remove

    def reverse_flows(self, go):
        """Reverse flows values of interest if needed"""
        self.CENTER_VORTEX *= go
        self.BORDER_VORTEX *= go
        self.BUILDING_OBSTACLE *= go

    # @cache
    def scout_enemy_opening(self, py_unit):
        enemy_start_pos = get_enemy_start_pos(self.agent)
        enemy_start_region = self.agent.region_manager.get_region(enemy_start_pos.as_tile())

        waypoint = get_closest(self.agent.region_manager.chokepoints_as_centers, enemy_start_pos)
        closest_choke = get_closest(
            self.agent.region_manager.chokepoints_as_centers,
            py_unit.position)
        cur_reg = self.agent.region_manager.get_region(py_unit.position)
        next_target_pos = get_closest(self.agent.non_start_bases_positions, enemy_start_pos)
        next_target_region = self.agent.region_manager.get_region(next_target_pos.as_tile())
        if (not self.switch_region and next_target_pos and closest_choke
                and py_unit.position.distance(closest_choke) > 3):
            if cur_reg == enemy_start_region:
                if (
                    self.agent.current_frame > self.frame_since_switch + SECOND_IN_FRAMES * 40
                    and self.changed_region
                ):
                    self.switch_the_region(next_target_region, waypoint)
                else:
                    if not self.changed_region:
                        self.notify_of_switch(waypoint)
                    self.do_pf(py_unit)
            elif cur_reg == next_target_region:
                self.do_pf(py_unit)
            else:
                self.normal_scout(py_unit, enemy_start_region, waypoint, enemy_start_pos)
        elif (next_target_pos and self.switch_region and closest_choke
              and py_unit.position.square_distance(closest_choke) > 3):
            if cur_reg == enemy_start_region:
                if (self.agent.current_frame > self.frame_since_switch + SECOND_IN_FRAMES * 10
                        and cur_reg == next_target_region and self.changed_region):
                    self.after_switch(enemy_start_region, waypoint)
                else:
                    if cur_reg == next_target_region and not self.changed_region:
                        self.notify_of_switch(waypoint)
                    self.do_pf(py_unit)
            elif cur_reg == next_target_region:
                if (
                    self.agent.current_frame > self.frame_since_switch + 16 * 10
                    and self.changed_region
                ):
                    self.after_switch(enemy_start_region, waypoint)
                else:
                    if not self.changed_region:
                        self.notify_of_switch(waypoint)
                    self.do_pf(py_unit)
            else:
                self.normal_scout(py_unit, enemy_start_region, waypoint, enemy_start_pos)
        elif not self.switch_region:
            # If not reach, move directly to enemy base
            self.target_region = enemy_start_region
            py_unit.move(enemy_start_pos)
        else:
            self.target_region = next_target_region
            py_unit.move(next_target_pos)

        if next_target_pos:
            self.agent.map_tools.draw_circle(next_target_pos, 5, Color(255, 165, 0))

    def normal_scout(self, py_unit, enemy_start_region, waypoint, enemy_start_pos):
        self.target_region = enemy_start_region
        self.add_attract_point(waypoint)
        py_unit.move(enemy_start_pos)

    def notify_of_switch(self, waypoint):
        self.attract_points.remove(waypoint)
        self.changed_region = True
        self.frame_since_switch = self.agent.current_frame

    def after_switch(self, enemy_start_region, waypoint):
        self.switch_region = False
        self.changed_region = False
        self.target_region = enemy_start_region
        self.add_attract_point(waypoint)

    def switch_the_region(self, region: Region, waypoint):
        self.switch_region = True
        self.changed_region = False
        self.target_region = region
        self.add_attract_point(waypoint)  # is center
