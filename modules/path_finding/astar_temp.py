from modules.path_finding.vertex import Vertex
from library import Point2DI
from modules.py_unit import PyUnit
from modules.path_finding.vertex import Vertex
from modules.path_finding.custom_priority_queue import CustomPriorityQueue
from queue import PriorityQueue

import copy
import math
from queue import PriorityQueue

def a_star(start_point, goal_point, vertex_dict, open_set):
    #open_set = PriorityQueue()
    #open_set.put(start_vertex, 0)
    came_from = {}
    vertex_dict[start_point].f_value = vertex_dict[start_point].g_value + heuristic_cost_estimate(vertex_dict[start_point], vertex_dict[goal_point])
    closed_set = set()
    while not open_set.empty():
        _, current_point = open_set.get()

        if vertex_dict[current_point] == vertex_dict[goal_point]:
            return reconstruct_path(came_from, current_point)

        for neighbor in get_neigbours(current_point, vertex_dict):
            current_g_score = vertex_dict[current_point].g_value + heuristic_cost_estimate(vertex_dict[current_point], vertex_dict[neighbor])

            '''if current_g_score < vertex_dict[neighbor].g_value:
                if vertex_dict[neighbor].g_value <= current_g_score:
                    continue
                elif vertex_dict[neighbor] in closed_set: 
                    if vertex_dict[neighbor].g_value <= current_g_score:
                        continue
                    else:
                        open_set.put((vertex_dict[neighbor].f_value, neighbor))'''
            if vertex_dict[neighbor].g_value > current_g_score:
                came_from[neighbor] = current_point
                vertex_dict[neighbor].g_value = current_g_score
                vertex_dict[neighbor].f_value = vertex_dict[neighbor].g_value + heuristic_cost_estimate(vertex_dict[neighbor], vertex_dict[goal_point])
                if neighbor not in open_set:
                    open_set.put((vertex_dict[neighbor].f_value, neighbor))

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

def scan_enemy_units(vertex_dict, enemy_units):
    for current_point in vertex_dict:
        current_vertex = vertex_dict[current_point]
        closest_distance = float('inf')
        for enemy_unit in enemy_units:
            distance = math.sqrt((current_vertex.x - enemy_unit.x) ** 2 + (current_vertex.y - enemy_unit.y) ** 2)
            if distance < closest_distance:
                closest_distance = distance
        if closest_distance <= 4:
            if closest_distance <= 1:
                current_vertex.g_value = 50
            elif closest_distance <= 2:
                current_vertex.g_value = 30
            elif closest_distance <= 3:
                current_vertex.g_value = 15
            else:
                current_vertex.g_value = 10


