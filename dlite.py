from library import Point2DI
from modules.py_unit import PyUnit
from vertex import Vertex
from custom_priority_queue import CustomPriorityQueue
import copy
import math


#Function for calculatoing heuristic. In this case using the Manhattan distance.
def calculateHeuristic(first_vertex : Vertex, second_vertex: Vertex):
    Vertex.distance = lambda self, other: abs(self.position_x - other.position_x) + abs(self.position_y - other.position_y)
    return first_vertex.distance(second_vertex)


def calculateKey(vertexes: dict, current_point: (int, int), start_point: (int, int), key_m):
    print("vertex: ", vertexes[current_point])
    print("rhs: ", vertexes[current_point].rhs_value)
    print("g:", vertexes[current_point].g_value) 

    kv_0 = min(vertexes[current_point].g_value, vertexes[current_point].rhs_value) + calculateHeuristic(vertexes[current_point], vertexes[start_point]) + key_m
    kv_1 = min(vertexes[current_point].g_value, vertexes[current_point].rhs_value)
    return (kv_0, kv_1)

def updateVertex(priority_queue : CustomPriorityQueue, vertexes : dict, current_point : (int, int), start_point : (int, int), target_point : (int, int), key_m):
    if(vertexes[current_point] != vertexes[target_point]):
        #tror den ska calculata avståndet för alla grannar till current_vertex och den minsta blir rhs väedet för current_vertex.
        vertexes[current_point].rhs_value = min([vertexes[neighbour].g_value + calculateHeuristic(vertexes[current_point], vertexes[neighbour]) for neighbour in vertexes[current_point].neighbour_list])    
    if(vertexes[current_point] in priority_queue):
        priority_queue.get(vertexes[current_point])
    if(vertexes[current_point].g_value != vertexes[current_point].rhs_value):
       
        priority_queue.put((calculateKey(vertexes, start_point, current_point, key_m), current_point))
       

def computeShortestPath(priority_queue : CustomPriorityQueue, vertexes : dict, start_point : (int, int), target_point : (int, int), key_m):
    top_element = priority_queue.get()
    top_key = top_element[0]
    top_point = top_element[1]
    
   
    priority_queue.put((calculateKey(vertexes, target_point, start_point, key_m), top_point))
  

    while(top_key < calculateKey(vertexes, start_point, start_point, 0) or start_point.rhs_value != start_point.g_value):
        top_element = priority_queue.get()
        print("top element", top_element)
        key_old = top_element[0]

        top_point = top_element[1]
        print("innan ifsats  ", top_point)

        if(key_old < calculateKey(vertexes, top_point, start_point, key_m)):
            priority_queue.put((calculateKey(vertexes, top_point, start_point, key_m), top_point))
        
        elif(vertexes[top_point].g_value > vertexes[top_point].rhs_value):
            vertexes[top_point].g_value = vertexes[top_point].rhs_value
            for neighbour in vertexes[top_point].neighbour_list:
                updateVertex(priority_queue, vertexes, neighbour, start_point, target_point, key_m)
        else:
            vertexes[top_point].g_value = math.inf
            updateVertex(priority_queue, vertexes, top_point, start_point, target_point, key_m)
            for neighbour in vertexes[top_point].neighbour_list:
                updateVertex(priority_queue, vertexes, neighbour, start_point, target_point, key_m)


def scanMap(agent: 'BasicAgent', start_vertex : Vertex, goal_vertex : Vertex, k_m):
    pass



#Ändra datan från att skicka vertexes till att skicka postionen, ochs sedan hämta vertex från dicten.
def dLiteMain(agent : 'BasicAgent', start_point: (int, int), target_point: (int, int)):    
    priority_queue = CustomPriorityQueue()
    vertexes = copy.deepcopy(agent.vertex_dict)
    key_m = 0
    vertexes[target_point].rhs_value = 0
    priority_queue.put((calculateKey(vertexes, target_point, start_point, key_m), target_point))


    computeShortestPath(priority_queue, vertexes, start_point, target_point, key_m)
    while(vertexes[start_point] != vertexes[target_point]):
        if(vertexes[start_point].g_value == math.inf):
            return False
        next_vertex = min(vertexes[start_point].neighbour_list, key=lambda neighbour: vertexes[neighbour].g_value + calculateHeuristic(vertexes[start_point], vertexes[neighbour]), default=None)
        print("to move")
        agent.move.move(Point2DI(next_vertex.position))

