'''File for the SafeMove task. Added by Hannes Lundberg, hanlu520'''

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from modules.py_unit import PyUnit
    from agents.basic_agent import BasicAgent

from library import Point2DI, Point2D, PLAYER_ENEMY
from tasks.task import Task, Status

from modules.path_finding.astar_temp import a_star
from modules.path_finding.custom_priority_queue import CustomPriorityQueue
from modules.path_finding.vertex import Vertex
from modules.path_finding.helpers import *
from queue import PriorityQueue



class SafeMove(Task):
    """Task for moving a unit"""

    def __init__(self, pos: Point2D, prio: int, agent: BasicAgent):
        super().__init__(prio=prio, agent= agent, candidates=agent.COMBAT_TYPES)
        self.target = pos
        self.previous_pos: Optional[Point2D] = None
        self.fails: int = 0
        self.frame_counter = 0
        self.path = []
        self.old_enemy_group = set()
        self.temptarget = None
        

    def on_start(self, py_unit: PyUnit) -> Status:
        """
        Start or restart the task.
        :return: Status.DONE if the task is started.
        """
        
        self.old_enemy_group = self.agent.unit_collection.get_group(PLAYER_ENEMY)


        if self.agent.safe_path.get(self.target) is not None:
            self.path = self.agent.safe_path[self.target]
        else:
            self.update_path(py_unit)
        
        print(self.path)
        for i in self.path:
            self.agent.terrain_map[(i[0], i[1])] = 4
            
        py_unit.next = 2
        if py_unit.next >= len(self.path) - 1:
            py_unit.next = len(self.path) - 1
            self.temptarget = self.path[py_unit.next]
        else:
            self.temptarget = self.path[py_unit.next]
        self.agent.terrain_map[(self.temptarget[0], self.temptarget[1])] = 7
        py_unit.move(Point2D(self.temptarget[0], self.temptarget[1]))
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

            if self.frame_counter % 350 == 0:
                reset_board(self.agent)
                self.frame_counter = 0

            if self.frame_counter % 200 == 0:
                self.agent.safe_path[self.target] = None
                

            if self.frame_counter % 50 == 0:
                if len(self.old_enemy_group) != len(self.agent.unit_collection.get_group(PLAYER_ENEMY)):
                    get_enemies_to_mark(self.agent, self.agent.unit_collection.get_group(PLAYER_ENEMY))
                
                
            #Are we at the selected target yet, or at least very, very close?
            if self.agent.map_tools.get_ground_distance(py_unit.position, Point2D(self.temptarget[0], self.temptarget[1])) < 3:
                py_unit.next += 3
                if py_unit.next <= len(self.path):
                    py_unit.next = len(self.path) - 1
                    self.temptarget = self.path[py_unit.next]
             
                py_unit.move(Point2D(self.temptarget[0], self.temptarget[1]))
                #return Status.NOT_DONE
            
            if len(self.path) < 3: #Point2DI(self.temptarget[0], self.temptarget[1]) == Point2DI(self.target):#self.agent.map_tools.get_ground_distance(Point2D(self.temptarget[0], self.temptarget[1]), self.target) < 1:
                self.agent.safe_path[self.target] = None
                py_unit.next = 10
                print("done")
                py_unit.stop
                return Status.DONE

            return Status.NOT_DONE
        else:
            self.agent.safe_path[self.target] = None
            py_unit.next = 10
            return Status.FAIL

    def update_path(self, py_unit: PyUnit):
        start_position = (int(round(py_unit.position.x)), int(round(py_unit.position.y)))
        target_position = (int(round(self.target.x)), int(round(self.target.y)))   

        self.path = a_star(start_position, target_position, self.agent.vertex_dict, self.agent)
        self.agent.safe_path[self.target] = self.path
