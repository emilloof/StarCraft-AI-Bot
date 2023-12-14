import math



class Vertex():
    def __init__(self, position : (int, int), child=None, edge_cost = 1, rhs_value=math.inf, g_value=math.inf, f_value = math.inf, neighbour_list=None) -> None:
        self.child = child
        self.position = position 
        self.x = position[0]
        self.y = position[1]
        self.edge_cost = edge_cost
        self.rhs_value = rhs_value
        self.g_value = g_value
        self.f_value = f_value
        #self.neighbour_list = []
        #self.neighbours()

    def build_path(self):
        if(self.child is None):
            return [self]
        return [self.child] + self.child.build_path()

    '''def neighbours(self):
        #from agents.basic_agent import BasicAgent
       # agent = BasicAgent()
        for x_cord in range(self.position_x - 1, self.position_x + 2):
            for y_cord in range(self.position_y - 1, self.position_y + 2):
                if((x_cord != self.position_x and y_cord != self.position_y)): #and agent.map_tools.is_walkable(x_cord, y_cord)):
                    current_neighbour = (x_cord, y_cord)
                    self.neighbour_list.append(current_neighbour)
        return self.neighbour_list
    '''

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, tuple):
            return self.x == other[0] and self.y == other[1]
        return False
        
    def __hash__(self) -> int:
        return hash((self.x, self.y))

                
    