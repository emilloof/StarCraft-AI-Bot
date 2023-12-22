from modules.path_finding.vertex import Vertex
from library import Point2DI
from modules.py_unit import PyUnit
from modules.path_finding.vertex import Vertex
from modules.path_finding.custom_priority_queue import CustomPriorityQueue
from queue import PriorityQueue

import copy
import math
from queue import PriorityQueue
from timeit import default_timer as timer

def a_star(start_point, goal_point, vertex_dict, open_set):
    start_time = timer()

    came_from = {}
    g_value = {vertex: float('inf') for vertex in vertex_dict}
    f_value = g_value

    g_value[start_point] = 0
    f_value[start_point] = heuristic_cost_estimate(vertex_dict[start_point], vertex_dict[goal_point])

    while not open_set.empty():
        _, current_point = open_set.get()

        if current_point == goal_point:
            end_time = timer()
            #print(f"astar took {end_time - start_time} seconds")

            return reconstruct_path(came_from, current_point)

        for neighbor in get_neigbours(current_point, vertex_dict):
            current_g_score = g_value[current_point] + heuristic_cost_estimate(vertex_dict[current_point], vertex_dict[neighbor])

            if g_value[neighbor] > current_g_score:
                came_from[neighbor] = current_point
                g_value[neighbor] = current_g_score
                f_value[neighbor] = g_value[neighbor] + heuristic_cost_estimate(vertex_dict[neighbor], vertex_dict[goal_point])*vertex_dict[neighbor].potential 
                #if neighbor not in open_set:
                open_set.put((f_value[neighbor], neighbor))

    return None



def heuristic_cost_estimate(vertex, goal_vertex):
    return math.sqrt((vertex.x - goal_vertex.x) ** 2 + (vertex.y - goal_vertex.y) ** 2)

def reconstruct_path(came_from, current_vertex):
    path = [current_vertex]
    while current_vertex in came_from:
        current_vertex = came_from[current_vertex]
        path.append(current_vertex)
    path.reverse()

    return path

def get_neigbours(current_point, vertex_dict):
    neighbour_list = []
    current_x = vertex_dict[current_point].x 
    current_y = vertex_dict[current_point].y

    for x_cord in range(current_x - 1, current_x + 2):
        for y_cord in range(current_y - 1, current_y + 2):
            if((current_x, current_y) != (x_cord, y_cord)): 
                current_neighbour = vertex_dict.get((x_cord, y_cord))
                if(current_neighbour != None):
                    neighbour_list.append((current_neighbour.x, current_neighbour.y))
    
    return neighbour_list
