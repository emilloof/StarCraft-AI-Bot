from __future__ import annotations
from typing import TYPE_CHECKING

from config import TIME_KEEP_ENEMY, TIME_KEEP_ENEMY_BUILDING, DEBUG_SCOUT, FRAME_SKIP_SCOUT, OLD_ENEMIES_ENABLED, FRAME_SKIP_SCOUT
from modules.extra import get_closest, get_enemy_start_pos

from modules.potential_flow.regions import Region
from modules.potential_flow.potentials import calculate_pval
from modules.potential_flow.vector import Vector
from tasks.task import Status
from tasks.scout import Scout
from modules.py_unit import PyUnit
from modules.extra import get_enemies_in_base_location, get_enemies_in_neighbouring_tiles
from library import Unit, Point2D, Point2DI, Color, PLAYER_ENEMY
from queue import SimpleQueue
from modules.cache_manager import add_expire_instance, add_expire_function, update_my_functions
from functools import cache

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent


SECOND_IN_FRAMES = 16
CHOKE_DIST = 5


class PFscout(Scout):

    def __init__(self, scout_bases: SimpleQueue[Point2D], prio: int, agent: BasicAgent):
        super().__init__(None, prio, agent, restart_on_fail=False, is_high_freq=True)
        # super().__init__(scout_bases, prio, agent)
        self.target_region: Region = None
        self.go = 1    # 1: proceed forward, -1: reverse direction
        self.last_reverse_frame = 0

        self.CENTER_VORTEX = 19
        self.CENTER_SOURCE_SINK = 3
        self.DISTANCE_TO_SWITCH_SOURCE_SINK = 4
        self.DISTANCE_TO_ACTIVE_BORDER_FLOW = 3
        self.BORDER_VORTEX = -16
        self.BORDER_SOURCE = 9
        self.BUILDING_OBSTACLE = 5
        self.ENEMY_NEEDLE = 9

        self.USE_ATTRACT_PVAL = True

        self.enemies = set()
        self.attract_points: set[Point2D] = set()

        self.frame_since_switch = 0
        self.switch_region = False
        self.changed_region = False

        self.use_border = True

        self.did_pf = False

        self.use_old_next_target_method = False

        self.USE_EXTRA_ATTR = True
        self.CTR = 19

        self.show_object_r = True
        self.show_unit_p = True
        self.show_region_p = True
        self.show_border_p = True
        self.show_all_p = False

        self.perma_use = True


        add_expire_instance(self.agent, self)
        add_expire_function(self.agent, self, self.get_next_target, 200)

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

        self.reg10 = next(region for region in self.agent.region_manager.regions if region.id == 10)

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
        if self.agent.scout_tester_1.scout != self:
            self.agent.scout_tester_1.scout = self

        self.CENTER_VORTEX = self.CTR
        self.CENTER_SOURCE_SINK = 3
        self.DISTANCE_TO_SWITCH_SOURCE_SINK = 4
        self.DISTANCE_TO_ACTIVE_BORDER_FLOW = 3
        self.BORDER_VORTEX = -16
        self.BORDER_SOURCE = 9
        self.BUILDING_OBSTACLE = 5
        self.ENEMY_NEEDLE = 9

        self.agent.latest_pfscout_unit = py_unit

        self.agent.scout_tile = py_unit.tile_position

        self.scout_enemy_opening(py_unit)

        if self.tt:
            self.agent.map_tools.draw_tile(self.tt)

        if OLD_ENEMIES_ENABLED:
            self.fade_enemies()    # should (according *) be at top of do_pf()

        update_my_functions(self.agent, self)

        if self.did_pf:
            ic("Did PF", self.agent.current_frame)
        else:
            ic("NOT", self.agent.current_frame)

        self.did_pf = False
        self.USE_ATTRACT_PVAL = self.perma_use

        return Status.NOT_DONE


    # @profile(immediate=True)
    def do_pf(self, py_unit):
        # Control scout's movement using potential flow
        self.did_pf = True
        self.move(py_unit)

        if DEBUG_SCOUT:
            self.debug(py_unit)

    def debug(self, py_unit: PyUnit):
        if self.show_object_r:
            if self.target_region:
                cur_center = self.target_region.center
                # self.agent.map_tools.draw_circle(cur_center, 3, Color.RED)
                self.agent.map_tools.draw_text(cur_center, "thres", Color.GRAY)
                self.agent.map_tools.draw_circle(Point2D(cur_center.x, cur_center.y - 1), self.DISTANCE_TO_SWITCH_SOURCE_SINK,
                                                 Color.GRAY)
            for obj in self.obstacles_debug:
                self.agent.map_tools.draw_circle(obj[0].position, obj[1], Color.TEAL)
                self.agent.map_tools.draw_text(obj[0].position, "o", Color.TEAL)
        scout_pos = py_unit.position
        if self.show_unit_p:
            light_red = Color(255, 204, 203)
            for up in self.unit_potentials:
                self.agent.map_tools.draw_text(up + scout_pos, "u", light_red)
                self.agent.map_tools.draw_line(scout_pos, up + scout_pos, light_red)
                self.agent.map_tools.draw_circle(up + scout_pos, 2, light_red)

        if self.show_region_p:
            for rp in self.region_potentials:
                self.agent.map_tools.draw_line(scout_pos, rp + scout_pos, Color.YELLOW)
                self.agent.map_tools.draw_circle(rp + scout_pos, 2, Color.YELLOW)

        if self.show_border_p:
            for bp in self.border_potentials:
                self.agent.map_tools.draw_line(scout_pos, bp + scout_pos, Color(255, 165,
                                                                                0))    # orange
                self.agent.map_tools.draw_circle(bp + scout_pos, 2, Color(255, 165, 0))
                self.agent.map_tools.draw_text(bp + scout_pos, "b", Color.WHITE)

        if self.show_all_p:
            for p in self.all_potentials:
                self.agent.map_tools.draw_line(scout_pos, p + scout_pos, Color.BLACK)
                self.agent.map_tools.draw_circle(p + scout_pos, 2, Color.BLACK)

    def near_reach_pos(self, pos1, pos2, dist=1):
        return pos1.distance(pos2) < dist

    def move(self, py_unit: PyUnit):
        # Code for controlling scout's movement using potential flow

        scout_pos = py_unit.unit.position

        if not (self.agent.current_frame % FRAME_SKIP_SCOUT == 0
                or self.near_reach_pos(scout_pos, self.scout_target)):
            return    # do nothing

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
        
        # idk
        self.go = 1

        self.scout_target = scout_pos + speed

        ratio = 1 / speed.length()
        seg = speed * ratio
        this_target = (seg * 3) + this_target
        while not self.agent.map_tools.is_walkable(Point2DI(this_target)):
            this_target = seg + this_target

            if self.agent.map_tools.is_valid_position(this_target):
                break

        if DEBUG_SCOUT:
            self.tt = Point2DI(this_target)
            # self.agent.map_tools.draw_text(self.scout_target, "scout_target", Color.WHITE)
            # self.agent.map_tools.draw_tile(Point2DI(this_target))
            # self.agent.map_tools.draw_text(py_unit.position, "scout", Color.WHITE)

        py_unit.move(this_target)

    def register_enemy_positions(self, enemies: set[Union[Unit, PyUnit]]):
        for enemy in enemies:

            if OLD_ENEMIES_ENABLED:
                if enemy in self.enemies:
                    enemy.last_seen = self.agent.current_frame
                else:
                    enemy.fade_time = (TIME_KEEP_ENEMY_BUILDING
                                       if enemy.unit_type.is_building else TIME_KEEP_ENEMY)

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
    
    def in_danger(self, py_unit: PyUnit) -> bool:
        """Check if unit is in danger"""
        if get_enemies_in_neighbouring_tiles(self.agent, py_unit.tile_position, dist=6):
            self.USE_ATTRACT_PVAL = False
            return True
        if danger := any(enemy.get_target() == py_unit for enemy in get_enemies_in_neighbouring_tiles(self.agent, py_unit.tile_position, dist=py_unit.unit_type.sight_range+2)):
            self.USE_ATTRACT_PVAL = False
            return danger


    @cache
    def get_next_target(self, py_unit: PyUnit) -> Point2D:
        """Get next target position"""
        # TODO: Combine the returns

        # num_occupied = len(self.agent.base_location_manager.get_occupied_base_locations(PLAYER_ENEMY))

        return self.agent.base_location_manager.get_next_expansion(PLAYER_ENEMY).position

        # if num_occupied > 1:
        #    return self.agent.base_location_manager.get_next_expansion(PLAYER_ENEMY)
        # else:
        #    return None

        # if expansion_base != starting_base (i.e. there exists some expansion)
        return (
            next.position
            if (next := self.agent.base_location_manager.get_next_expansion(PLAYER_ENEMY))
            != self.agent.base_location_manager.get_player_starting_base_location(PLAYER_ENEMY)
            else None
        )

    @cache
    def get_next_target_old(self, py_unit: PyUnit) -> Point2D:
        """Get next target position"""
        closest_enemy_base = get_closest(
            self.agent.non_start_bases, get_enemy_start_pos(
                self.agent), lambda base: base.position)
        if not self.use_old_next_target_method:
            if closest_enemy_base.contains_position(
                    py_unit.position):  # maybe use is_visible instead
                # if enemy base has resource depot/town hall, then consider it as a base
                # target (scout the base)
                if any(
                        unit.unit_type.is_resource_depot
                        for unit in get_enemies_in_base_location(self.agent, closest_enemy_base)):
                    return closest_enemy_base.position
                else:
                    return None
        return closest_enemy_base.position

    @cache
    def validate_expansion_target(self, next_target_pos: Point2D, switch: callable = None) -> bool:
        """Validate expansion target"""
        target_base = get_closest(
            self.agent.non_start_bases,
            next_target_pos,
            lambda base: base.position)
        if self.agent.map_tools.is_visible(int(next_target_pos.x), int(next_target_pos.y)) \
                and target_base not in self.agent.base_location_manager.get_occupied_base_locations(PLAYER_ENEMY):
            # switch() : lambda: self.switch_the_region(enemy_start_region, waypoint)
            return False
        return True

        # id = 10
    
        # GÅ o lägg
        # NÅGOT FEL MED cur_reg varken likam ed enemy start eller next?? (kolla i visualdebugger) det tog ett tag foö skiten o dyka uipp
    def scout_enemy_opening(self, py_unit):
        enemy_start_pos = get_enemy_start_pos(self.agent)
        enemy_start_region = self.agent.region_manager.get_region(enemy_start_pos.as_tile())

        waypoint = get_closest(self.agent.region_manager.chokepoints_as_centers, enemy_start_pos)
        closest_choke = get_closest(self.agent.region_manager.chokepoints, py_unit.position,
                                    lambda c: c.center)
        closest_choke = closest_choke.center

        cur_reg = self.agent.region_manager.get_region(py_unit.tile_position)

        next_target_pos = self.agent.base_location_manager.get_next_expansion(PLAYER_ENEMY).position
        if next_target_pos not in {enemy_start_pos, self.reg10.center} and enemy_start_pos == Point2D(24.25, 139.5):
            next_target_pos = self.reg10.center
        if next_target_pos:
            next_target_region = self.agent.region_manager.get_region(next_target_pos.as_tile())

        if (not self.switch_region and closest_choke and next_target_pos
                and py_unit.position.distance(closest_choke) > CHOKE_DIST):
            if cur_reg == enemy_start_region:
                if (self.agent.current_frame > self.frame_since_switch + SECOND_IN_FRAMES * 40
                        and self.changed_region):
                    self.switch_the_region(next_target_region, waypoint)
                else:
                    if not self.changed_region:
                        self.notify_of_switch(waypoint)
                    self.do_pf(py_unit)
            elif cur_reg == next_target_region:
                self.do_pf(py_unit)
            else:
                self.normal_scout(py_unit, enemy_start_region, waypoint, enemy_start_pos)
        elif (self.switch_region and closest_choke and next_target_pos
              and py_unit.position.square_distance(closest_choke) > CHOKE_DIST):
            if cur_reg == enemy_start_region:
                if (self.agent.current_frame > self.frame_since_switch + SECOND_IN_FRAMES * 10
                        and cur_reg == next_target_region and self.changed_region):
                    self.after_change(enemy_start_region, waypoint)
                else:
                    if cur_reg == next_target_region and not self.changed_region:
                        self.notify_of_switch(waypoint)
                    self.do_pf(py_unit)
            elif cur_reg == next_target_region:
                if (self.agent.current_frame > self.frame_since_switch + SECOND_IN_FRAMES * 10
                        and self.changed_region):
                    self.after_change(enemy_start_region, waypoint)
                else:
                    if not self.changed_region:
                        self.notify_of_switch(waypoint)
                    self.do_pf(py_unit)
            else:
                # TODO: check if enemies close first
                self.normal_scout(py_unit, enemy_start_region, waypoint, next_target_pos)
        elif not self.switch_region:
            # If not reach, move directly to enemy base
            self.target_region = enemy_start_region
            #if self.in_danger(py_unit):
            #    self.do_pf(py_unit)
            #    return
            py_unit.move(enemy_start_pos)
            # self.add_attract_point(enemy_start_pos)
            self.tt = Point2DI(enemy_start_pos)
        else:
            if not next_target_pos:
                raise ValueError("No next target pos")
            self.target_region = next_target_region
            
            #if self.in_danger(py_unit):
            #    self.do_pf(py_unit)
            #    return
            py_unit.move(next_target_pos)
            # self.add_attract_point(next_target_pos)
            self.tt = Point2DI(next_target_pos)

        if DEBUG_SCOUT:
            self.agent.map_tools.draw_circle(closest_choke, 0.25, Color.PURPLE)
            if next_target_pos:
                # self.agent.map_tools.draw_circle(next_target_pos, 6, Color.PURPLE)
                self.agent.map_tools.draw_circle(next_target_pos, 5, Color(255, 165, 0))
                self.agent.map_tools.draw_text(next_target_pos, "next", Color.WHITE)
        

    def normal_scout(self, py_unit, enemy_start_region, waypoint, pos):
        self.target_region = enemy_start_region
        self.add_attract_point(waypoint)
        if self.in_danger(py_unit):
            self.do_pf(py_unit)
            return
        py_unit.move(pos)
        self.tt = Point2DI(pos)

    def notify_of_switch(self, waypoint):
        self.attract_points.remove(waypoint)
        self.changed_region = True
        # self.validate_expansion_target.cache_clear()
        self.frame_since_switch = self.agent.current_frame

    def after_change(self, enemy_start_region, waypoint):
        self.switch_region = False
        self.changed_region = False
        self.target_region = enemy_start_region
        self.add_attract_point(waypoint)

    def switch_the_region(self, region: Region, waypoint):
        self.switch_region = True
        self.changed_region = False
        self.target_region = region
        self.add_attract_point(waypoint)    # is center
