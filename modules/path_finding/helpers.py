'''File for the helpers for setting potentials. Added by Hannes Lundberg, hanlu520'''
from modules.path_finding.vertex import Vertex

def get_potential(vertex):
    return vertex.potential

def set_potential(vertex, potential):
    vertex.potential = potential
    return vertex.potential

def set_vertex_potential(agent, vertex, potential_value, radius):
    # Set the potential of the vertex itself
    set_potential(vertex, potential_value)
    agent.used_vertexes.append(vertex)

    # Define the range of layers to iterate over
    if radius <= 1:
        layers = range(1, 2)
    else:
        layers = range(1, radius)
    
    for layer in layers:
        for x in range(vertex.x - layer, vertex.x + layer + 1):
            for y in range(vertex.y - layer, vertex.y + layer + 1):
                # Exclude vertices that are not in the current layer
                if x == vertex.x - layer or x == vertex.x + layer or y == vertex.y - layer or y == vertex.y + layer:
                    if agent.vertex_dict.get((x,y)) is not None:
                        neighbour_vertex = agent.vertex_dict[(x,y)]
                        pot = set_potential(neighbour_vertex, potential_value - layer)
                        agent.used_vertexes.append(neighbour_vertex)
                        agent.terrain_map[(x,y)] = pot

def get_enemies_to_mark(agent, enemies : dict):
    for enemy in enemies:
        enemy_pos = enemy.tile_position
        attack_rng = enemy.unit_type.attack_range
        is_combat_unit = enemy.unit_type.is_combat_unit
        is_building = enemy.unit_type.is_building
   

        if is_combat_unit and not is_building:
            if agent.vertex_dict.get(enemy_pos) is None:
                agent.vertex_dict[enemy_pos] = Vertex((enemy_pos.x, enemy_pos.y))
            set_vertex_potential(agent, agent.vertex_dict[enemy_pos], 100, int(round(attack_rng)))

def reset_board(agent):
    for vertex in agent.used_vertexes:
        set_potential(vertex, 0)
    agent.used_vertexes = []