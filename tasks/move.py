from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from modules.py_unit import PyUnit
    from agents.basic_agent import BasicAgent

from library import Point2D
from tasks.task import Task, Status

#added by hanlu520
from modules.path_finding.custom_priority_queue import CustomPriorityQueue
from modules.path_finding.vertex import Vertex
from modules.path_finding.lpa_star import *
import copy


class Move(Task):
    """Task for moving a unit"""

    def __init__(self, pos: Point2D, prio: int, agent: BasicAgent):
        super().__init__(prio=prio, agent= agent, candidates=agent.COMBAT_TYPES)
        self.target = pos
        self.previous_pos: Optional[Point2D] = None
        self.fails: int = 0
        self.frame_counter = 0
        self.agent = agent        
        

    def on_start(self, py_unit: PyUnit) -> Status:
        """
        Start or restart the task.
        :return: Status.DONE if the task is started.
        """
        #- init for LPA* - hanlu520
        start_position = (int(round(py_unit.position.x)), int(round(py_unit.position.y)))
        target_position = (int(round(self.target.x)), int(round(self.target.y)))    
        print("STARTPOS_ ", start_position)
        print("MÅLPOS_ ", target_position)
        if(not self.agent.map_tools.is_walkable(start_position[0], start_position[1])):
            print("Startpositionen är inte walkable")
            return Status.FAIL

        priority_queue = CustomPriorityQueue()
        secondary_queue = []
        vertexes = copy.copy(self.agent.vertex_dict)
        vertexes[start_position].rhs_value = 0
        #self.agent.vertex_dict[start_position].parent = None
        vertexes[target_position].child = None

        if(not self.agent.map_tools.is_walkable(start_position[0], start_position[1])):
            print("Startpositionen är inte walkable")
            return Status.FAIL

        initial_key_value = calculateKey(vertexes, start_position, target_position)
        priority_queue.put((initial_key_value, start_position))
        # secondary_queue.append((initial_key_value, start_position))
        path = computeShortestPath(priority_queue, secondary_queue, vertexes, start_position, target_position)
        print("PATH_ ", path)

        py_unit.move(self.target)
        self.previous_pos = py_unit.position
        return Status.DONE

    
    
    
    
    
    def on_step(self, py_unit: PyUnit) -> Status:
        """
        Checks if the task is continuing.
        
        :return: Status.DONE when unit is very close to the target (<1 tile). Status.NOT_DONE is
        unit is still on the move. Status.FAIL if unit is dead, idle have been stuck for >5 ticks.
        """
        self.frame_counter += 1

        if py_unit.is_idle:
            return Status.FAIL
        if py_unit.is_alive:
            # Are we at the selected target yet, or at least very, very close?
            
            if(self.agent.map_tools.get_ground_distance(py_unit.position, self.target) < 1):
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
