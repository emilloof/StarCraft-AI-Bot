from library import Point2D
from modules.py_unit import PyUnit
from modules.path_finding.vertex import Vertex
from modules.path_finding.custom_priority_queue import CustomPriorityQueue
import copy
import math





def neighbouringVertexes(current_vertex : Vertex, vertexes : dict):
    neighbour_list = []
    for x_cord in range(current_vertex.position_x - 1, current_vertex.position_x + 2):
        for y_cord in range(current_vertex.position_y - 1, current_vertex.position_y + 2):
            if((current_vertex.position_x, current_vertex.position_y) != (x_cord, y_cord)): 
                current_neighbour = vertexes.get((x_cord, y_cord))
                if(current_neighbour != None):
                    neighbour_list.append((current_neighbour.position_x, current_neighbour.position_y))
    return neighbour_list
'''
def calculateHeuristic(first_vertex : Vertex, second_vertex: Vertex):
    Vertex.distance = lambda self, other: abs(self.position_x - other.position_x) + abs(self.position_y - other.position_y)
    return first_vertex.distance(second_vertex)
'''

def calculateHeuristic(first_vertex: Vertex, second_vertex: Vertex):
    Vertex.distance = lambda self, other: math.sqrt((self.position_x - other.position_x)**2 + (self.position_y - other.position_y)**2)
    return first_vertex.distance(second_vertex)


def calculateKey(vertexes: dict, current_point: (int, int), goal_point: (int, int)):
    kv_0 = min(vertexes[current_point].g_value, vertexes[current_point].rhs_value) + calculateHeuristic(vertexes[current_point], vertexes[goal_point])
    kv_1 = min(vertexes[current_point].g_value, vertexes[current_point].rhs_value)
    return (kv_0, kv_1)

def updateVertex(priority_queue : CustomPriorityQueue, secondary_queue : list, vertexes : dict, current_point : (int, int), start_point : (int, int), goal_point : (int, int)):
        neighbour_list = neighbouringVertexes(vertexes[current_point], vertexes)
        if(vertexes[current_point] != vertexes[start_point]):
            lowest_value = math.inf
            for neighbour in neighbour_list:
                neighbour_value = vertexes[neighbour].g_value + calculateHeuristic(vertexes[current_point], vertexes[neighbour])
                if(neighbour_value < lowest_value):
                    lowest_value = neighbour_value
            vertexes[current_point].rhs_value = lowest_value
        if(vertexes[current_point].g_value != vertexes[current_point].rhs_value):
            # curr_point = (5, 5)
            # start_point = (1, 2)
            # goal_point = (10, 10)

            priority_queue.update((calculateKey(vertexes, current_point, goal_point), current_point))
            # ((15, 0), vertex.point)

            


def computeShortestPath(priority_queue : CustomPriorityQueue, secondary_queue: list, vertexes : dict, start_point : (int, int), goal_point : (int, int)):
        top_element = priority_queue.peek()
        top_key = top_element[0]
        top_point = top_element[1]
        while(top_key < calculateKey(vertexes, goal_point, goal_point) or vertexes[goal_point].rhs_value != vertexes[goal_point].g_value):
            print("fast här")
            
            parent_point = top_point
            
            
            #print("top_point", top_point)
            
            """while(True):
                print("i true loopen")
                if(priority_queue.peek() not in secondary_queue):
                    priority_queue.get()
                else:
                    break"""
            
            top_element = priority_queue.get()
            top_key = top_element[0]
            top_point = top_element[1]
            #secondary_queue.remove((top_key, top_point))
            
            
            vertexes[parent_point].child = vertexes[top_point]
            
            if(top_point == goal_point): 
                print("goal found", top_point)
                return vertexes[top_point].build_path()
           
            #print(vertexes[top_point].parent)
           
            if(vertexes[top_point].g_value > vertexes[top_point].rhs_value):
                vertexes[top_point].g_value = vertexes[top_point].rhs_value
                neighbour_list = neighbouringVertexes(vertexes[top_point], vertexes)
                for neighbour in neighbour_list:
                    updateVertex(priority_queue, secondary_queue, vertexes, neighbour, start_point, goal_point)
           
            else:
                vertexes[top_point].g_value = math.inf
                neighbour_list = neighbouringVertexes(vertexes[top_point], vertexes)
                neighbour_list.append(top_point)
                for neighbour in neighbour_list:
                    updateVertex(priority_queue, secondary_queue, vertexes, neighbour, start_point, goal_point)
        return [] #return empty path if no path is found
     

def lpaMain(agent : 'BasicAgent', py_unit : PyUnit, start_point: (int, int), target_point: (int, int)):
    priority_queue = CustomPriorityQueue()
    secondary_queue = []
    vertexes = copy.deepcopy(agent.vertex_dict)
    vertexes[start_point].rhs_value = 0
    priority_queue.put((calculateKey(vertexes, start_point, target_point), start_point))
    secondary_queue.append((calculateKey(vertexes, start_point, target_point), start_point))
    
    
    while(start_point != target_point):
        path = computeShortestPath(priority_queue, secondary_queue, vertexes, start_point, target_point)
        print("path", path)
        for i in range(len(path)):
            next_vertex = path[i]
            next_point = (next_vertex.position_x, next_vertex.position_y)
            start_point = next_point
            py_unit.move(Point2D(next_point[0], next_point[1]))
        #computeShortestPath()
    print("done")

