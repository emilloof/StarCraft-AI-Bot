import math




class Vertex():
    def __init__(self, position : (int, int), edge_cost = 1, potential=0, neighbour_list=None) -> None:
        self.position = position 
        self.x = position[0]
        self.y = position[1]
        self.edge_cost = edge_cost
        self.potential = potential
        
        #self.g_value = g_value
        #self.f_value = f_value
        self.neighbour_list = []
        self.get_neighbours()
    

    def get_neighbours(self):
        from agents.basic_agent import BasicAgent

        current_x = self.x 
        current_y = self.y
        #walkable_tiles = BasicAgent.walkable_tiles
        #print("1212", walkable_tiles)

        for x_cord in range(current_x - 1, current_x + 2):
            for y_cord in range(current_y - 1, current_y + 2):
                #if BasicAgent.map_tools.is_walkable(x_cord, y_cord): 
                if (current_x, current_y) != (x_cord, y_cord): 
                    self.neighbour_list.append((x_cord, y_cord))


    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, tuple):
            return self.x == other[0] and self.y == other[1]
        return False
        
    def __hash__(self) -> int:
        return hash((self.x, self.y))

                
    