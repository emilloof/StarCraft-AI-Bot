from __future__ import annotations
from typing import TYPE_CHECKING

from pygame import Vector2
from config import TIME_KEEP_ENEMY, TIME_KEEP_ENEMY_BUILDING

from modules.potential_flow.regions import get_region
from modules.potential_flow.t_potential import calculate_pval
from tasks.task import Status
from tasks.scout import Scout

if TYPE_CHECKING:
    from modules.py_unit import PyUnit
    from agents.basic_agent import BasicAgent
    

from library import Unit, Point2D
from queue import SimpleQueue

class PotentialFlowScout(Scout):
    def __init__(self, scout_bases: SimpleQueue[Point2D], prio: int, agent: BasicAgent):
        super().__init__(scout_bases, prio, agent)
        self.target_region = None
        self.go = 1  # 1: proceed forward, -1: reverse direction

        self.CENTER_VORTEX = 600
        self.CENTER_SOURCE_SINK = 100
        self.DISTANCE_TO_SWITCH_SOURCE_SINK = 128
        self.DISTANCE_TO_ACTIVE_BORDER_FLOW = 96
        self.BORDER_VORTEX = -500
        self.BORDER_SOURCE = 300
        self.BUILDING_OBSTACLE = 150
        self.ENEMY_NEEDLE = 300

        self.enemies: dict[Unit, PyUnit] = dict()

        self.attract_points: set[Point2D] = set()

        #_unit_p = {}
        self.region_potentials: list[Vector2] = []
        self.border_potentials = []
        # _all_p = {}

    def register_enemy_positions(self, enemies):
        for enemy in enemies:
            fade_time = TIME_KEEP_ENEMY_BUILDING if enemy.unit_type.is_building else TIME_KEEP_ENEMY

            # TODO: update enemy position, in case Unit.position does not work
            if enemy in self.enemies:
                # update (idk if needed)
                self.enemies[enemy].unit = enemy
            else:
                self.enemies[enemy] = PyUnit(enemy, self.agent, last_seen=self.agent.current_frame, fade_time=fade_time)
    
    def get_enemies(self):
        return self.enemies
    
    def set_attract_points(self, attract_points):
        self.attract_points = attract_points

    def set_scout_target(self, scout_target):
        self.scout_target = scout_target
    
    def fade_enemies(self):
        for enemy_unit, enemy in self.enemies.items():
            if self.agent.current_frame - enemy.last_seen > enemy.fade_time: #or (not enemy_unit.is_valid and self.agent.map_tools.is_visible(enemy.tile_position))):
                self.enemies.pop(enemy_unit)


    def reverse_flows(self):
        """Reverse flows values of interest if needed"""
        self.CENTER_VORTEX *= self.go
        self.BORDER_VORTEX *= self.go
        self.BUILDING_OBSTACLE *= self.go

    def move(self, py_unit: PyUnit):
        # Code for controlling scout's movement using potential flow

        self.fade_enemies()

        # TODO: ADD IF CLOSE THEN DO THIS (NEAR)

        ###

        this_target = self.scout_target

        ###

        self.target_region = self.target_region if self.target_region else get_region(self.agent, self.agent.regions, self.scout_target) # use tile position?

        # reverse all flows values if needed
        self.reverse_flows()
        speed = calculate_pval(self.agent, self, py_unit)
        # reverse back
        self.reverse_flows()

        self.scout_target = py_unit.position + speed

        # Unsure if Vector2D.length() should be used
        ratio = 32.0 / speed.length()
        seg = speed * ratio
        this_target = seg * 3 + this_target
        while not self.agent.map_tools.is_walkable(this_target):
            this_target = seg + this_target

            if self.agent.map_tools.is_valid_position(this_target):
                pass
                # MAKE VALID?
                break
        
        py_unit.move(this_target)

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

        for tile in get_region(self.agent, self.agent.regions, py_unit.tile_position)[0]:
            self.agent.map_tools.draw_tile(tile)
        
        # Control scout's movement using potential flow
        self.move(py_unit)

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
        
    