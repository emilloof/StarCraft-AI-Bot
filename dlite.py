from library import Point2DI
from modules.py_unit import PyUnit
from vertex import Vertex
from custom_priority_queue import CustomPriorityQueue
import copy
import math



def neighbouringVertexes(current_vertex : Vertex, vertexes : dict):
    neighbour_list = []
    for x_cord in range(current_vertex.position_x - 1, current_vertex.position_x + 2):
        for y_cord in range(current_vertex.position_y - 1, current_vertex.position_y + 2):
            if((x_cord != current_vertex.position_x and y_cord != current_vertex.position_y)): 
                current_neighbour = vertexes.get((x_cord, y_cord))
                
                if(current_neighbour != None):
                    neighbour_list.append((current_neighbour.position_x, current_neighbour.position_y))
    return neighbour_list

#Function for calculatoing heuristic. In this case using the Manhattan distance.
def calculateHeuristic(first_vertex : Vertex, second_vertex: Vertex):
    Vertex.distance = lambda self, other: abs(self.position_x - other.position_x) + abs(self.position_y - other.position_y)
    return first_vertex.distance(second_vertex)


def calculateKey(vertexes: dict, current_point: (int, int), start_point: (int, int), key_m):
    kv_0 = min(vertexes[current_point].g_value, vertexes[current_point].rhs_value) + calculateHeuristic(vertexes[current_point], vertexes[start_point]) + key_m
    kv_1 = min(vertexes[current_point].g_value, vertexes[current_point].rhs_value)
    return (kv_0, kv_1)

def updateVertex(priority_queue : CustomPriorityQueue, vertexes : dict, current_point : (int, int), start_point : (int, int), target_point : (int, int), key_m):
    neighbour_list = neighbouringVertexes(vertexes[current_point], vertexes)
    
    if(vertexes[current_point] != vertexes[target_point]):
        print("in if1")
        #tror den ska calculata avståndet för alla grannar till current_vertex och den minsta blir rhs väedet för current_vertex.
        vertexes[current_point].rhs_value = min([vertexes[neighbour].g_value + calculateHeuristic(vertexes[current_point], vertexes[neighbour]) for neighbour in neighbour_list])    
    print(current_point in priority_queue)
    if(current_point in priority_queue):
        print("in if2")
        priority_queue.get(vertexes[current_point])
    if(vertexes[current_point].g_value != vertexes[current_point].rhs_value):
        print("in if3")
        priority_queue.put((calculateKey(vertexes, current_point, start_point, key_m), current_point))
       

def computeShortestPath(priority_queue : CustomPriorityQueue, vertexes : dict, start_point : (int, int), target_point : (int, int), key_m):
    
    top_element = priority_queue.get()
    top_key = top_element[0]
    top_point = top_element[1]
    
   
    priority_queue.put((calculateKey(vertexes, top_point, start_point, key_m), top_point))
    '''
    Fixa så priority_queue kan ta bort speicifika element.
    '''

    while(top_key < calculateKey(vertexes, start_point, start_point, 0) or vertexes[start_point].rhs_value != vertexes[start_point].g_value):
        top_element = priority_queue.get()
        #print("top_element", top_element)
        key_old = top_element[0]
        top_point = top_element[1]

        current_neighbour_list = neighbouringVertexes(vertexes[top_point], vertexes)
        #print("rhs: ", vertexes[top_point].rhs_value, "g: ", vertexes[top_point].g_value)
        #print("key_old: ", key_old, "key_new: ", calculateKey(vertexes, top_point, start_point, key_m))

        if(key_old < calculateKey(vertexes, top_point, start_point, key_m)):
            #print("in if första")
            priority_queue.put((calculateKey(vertexes, top_point, start_point, key_m), top_point))
        
        elif(vertexes[top_point].g_value > vertexes[top_point].rhs_value):
            #print("in elif")
            vertexes[top_point].g_value = vertexes[top_point].rhs_value
            for neighbour in current_neighbour_list:
                updateVertex(priority_queue, vertexes, neighbour, start_point, target_point, key_m)
        else:
            #print("in else")
            vertexes[top_point].g_value = math.inf
            updateVertex(priority_queue, vertexes, top_point, start_point, target_point, key_m)
            for neighbour in current_neighbour_list:
                updateVertex(priority_queue, vertexes, neighbour, start_point, target_point, key_m)


def scanMap(agent: 'BasicAgent', start_vertex : Vertex, goal_vertex : Vertex, k_m):
    pass


    
def dLiteMain(agent : 'BasicAgent', start_point: (int, int), target_point: (int, int)):    
    priority_queue = CustomPriorityQueue()
    vertexes = copy.deepcopy(agent.vertex_dict)
    key_m = 0
    vertexes[target_point].rhs_value = 0
    priority_queue.put((calculateKey(vertexes, target_point, start_point, key_m), target_point))


    computeShortestPath(priority_queue, vertexes, start_point, target_point, key_m)
    print("comupted shortest path klar")
    while(vertexes[start_point] != vertexes[target_point]):
        
        if(vertexes[start_point].g_value == math.inf):
            return False
        neighbour_list = neighbouringVertexes(vertexes[start_point], vertexes)
        next_vertex = min(neighbour_list, key=lambda neighbour: vertexes[neighbour].g_value + calculateHeuristic(vertexes[start_point], vertexes[neighbour]), default=None)
        print("to move")
        agent.move.move(Point2DI(next_vertex.position))

