from modules.path_finding.vertex import Vertex
from commandcenter import Point2DI
from modules.py_unit import PyUnit
from modules.path_finding.vertex import Vertex
from modules.path_finding.custom_priority_queue import CustomPriorityQueue
from queue import PriorityQueue

import copy
import math
from queue import PriorityQueue
from timeit import default_timer as timer

def a_star(start_point, goal_point, vertex_dict, agent):
    start_time = timer()
    open_set = PriorityQueue()
    open_set.put((0, start_point))
    came_from = {}
    init_timer = timer()
    g_value = {vertex: float('inf') for vertex in vertex_dict}
    f_value = g_value
    init_timer_end = timer()

    g_value[start_point] = 0
    f_value[start_point] = distance_estimate(vertex_dict[start_point], vertex_dict[goal_point])

    while not open_set.empty():
        _, current_point = open_set.get()

        if current_point == goal_point:
            end_time = timer()
            print(f"astar took {end_time - start_time} seconds")
            return reconstruct_path(came_from, current_point)
        neighbour_list = vertex_dict[current_point].neighbour_list
        for neighbor in neighbour_list:
            
            if agent.map_tools.is_walkable(neighbor[0], neighbor[1]):
                current_g_score = g_value[current_point] + distance_estimate(vertex_dict[neighbor], vertex_dict[goal_point]) + vertex_dict[neighbor].potential 
                if g_value[neighbor] > current_g_score:
                    came_from[neighbor] = current_point
                    f_value[neighbor] = g_value[neighbor] + distance_estimate(vertex_dict[neighbor], vertex_dict[goal_point]) + vertex_dict[neighbor].potential 
                    g_value[neighbor] = current_g_score

                    open_set.put((f_value[neighbor], neighbor))

    return None


def distance_estimate(vertex, goal_vertex):
    return math.sqrt((vertex.x - goal_vertex.x) ** 2 + (vertex.y - goal_vertex.y) ** 2)

def reconstruct_path(came_from, current_vertex):
    path = [current_vertex]
    while current_vertex in came_from:
        current_vertex = came_from[current_vertex]
        path.append(current_vertex)
    path.reverse()
    return path

