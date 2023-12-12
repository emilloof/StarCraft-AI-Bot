import math



class Vertex():
    def __init__(self, position : (int, int), child=None, rhs_value=math.inf, g_value=math.inf, neighbour_list=None) -> None:
        self.child = child
        self.position = position 
        self.position_x = position[0]
        self.position_y = position[1]
        self.rhs_value = rhs_value
        self.g_value = g_value
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
            return self.position_x == other.position_x and self.position_y == other.position_y
        elif isinstance(other, tuple):
            return self.position_x == other[0] and self.position_y == other[1]
        return False
        
    def __hash__(self) -> int:
        return hash((self.position_x, self.position_y))

                
    