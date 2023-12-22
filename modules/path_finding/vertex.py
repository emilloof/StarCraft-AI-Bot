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
        #self.neighbour_list = []
        #self.neighbours()
    
    '''

    def set_potential(self, potential):
        self.potential = potential

    
    def set_vertex_potential(self, value):
        from agents.basic_agent import BasicAgent
        # Set the potential of the vertex itself
        self.set_potential(value)

        # Define the range of layers to iterate over
        layers = range(1, 4)

        for layer in layers:
            # Calculate the potential for this layer
            layer_potential = value * (layer + 1)

            # Iterate over the vertices in this layer
            for x in range(self.x - layer, self.x + layer + 1):
                for y in range(self.y - layer, self.y + layer + 1):
                    # Exclude vertices that are not in the current layer
                    if x == self.x - layer or x == self.x + layer or y == self.y - layer or y == self.y + layer:
                        neighbour_vertex = BasicAgent.vertex_dict[(x,y)]
                        neighbour_vertex.set_potential(layer_potential)
    '''  

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, tuple):
            return self.x == other[0] and self.y == other[1]
        return False
        
    def __hash__(self) -> int:
        return hash((self.x, self.y))

                
    