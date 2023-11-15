from __future__ import annotations
from typing import TYPE_CHECKING
from library import Point2DI, Point2D
if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent

from library import PLAYER_SELF, PLAYER_NEUTRAL

# Skapad av eriei013 för testning av depth map
def print_depth(bottle_map: dict, heat_map_row: list, x: int, y: int) -> bool:
    var = False
    tile = Point2DI(x, y)
    if tile in bottle_map.get(7, []):
        heat_map_row.append(2)
        var = True
    elif tile in bottle_map.get(8, []):
        heat_map_row.append(3)
        var = True
    elif tile in bottle_map.get(9, []):
        heat_map_row.append(4)
        var = True
    elif tile in bottle_map.get(10, []):
        heat_map_row.append(5)
        var = True
    elif tile in bottle_map.get(11, []):
        heat_map_row.append(6)
        var = True
    elif tile in bottle_map.get(12, []):
        heat_map_row.append(7)
        var = True
    return var

# Skapad av eriei013 för testning av gate tiles
def print_gate_tiles(bottle_tiles: list, heat_map_row: list, x: int, y: int) -> bool:
    tile = Point2DI(x, y)

    """is_in_list = any(tile in sublist for sublist in bottle_tiles)
    if is_in_list:
        heat_map_row.append(2)
        return True
    return False"""
    if tile in bottle_tiles[0]:
        heat_map_row.append(2)
        return True
    if tile in bottle_tiles[1]:
        heat_map_row.append(3)
        return True
    if tile in bottle_tiles[2]:
        heat_map_row.append(4)
        return True
    if tile in bottle_tiles[3]:
        heat_map_row.append(5)
        return True
    if tile in bottle_tiles[4]:
        heat_map_row.append(6)
        return True
    if tile in bottle_tiles[5]:
        heat_map_row.append(7)
        return True
    return False


def debug_map(agent: BasicAgent, bottle_tiles: list) -> None:
    """Displays the map in a separate window."""
    """heat_map = [[int(agent.map_tools.is_walkable(x, y)) for x in range(agent.map_tools.width)]
                for y in range(agent.map_tools.height)]"""
    heat_map = []
    #print(bottle_tiles)
    for y in range(agent.map_tools.height):
        heat_map_row = []
        for x in range(agent.map_tools.width):
            if int(agent.map_tools.is_walkable(x, y)):
                b = False
                #b = print_depth(bottle_tiles, heat_map_row, x, y) # Avkommentera denna rad om du vill ha ursprungsfunktionaliteten (Används av eriei013)
                b = print_gate_tiles(bottle_tiles, heat_map_row, x, y) # Avkommentera denna rad om du vill ha ursprungsfunktionaliteten (Används av eriei013)
                #print(bottle_tiles)
                if not b:
                    heat_map_row.append(1)
            else:
                heat_map_row.append(0)
        heat_map.append(heat_map_row)
            
    agent.debugger.set_display_values(heat_map)


def debug_text(agent: BasicAgent) -> None:
    """Displays text on screen with information about build order and tasks."""
    agent.map_tools.draw_text_screen(.01, .01, f"Build order: {agent.build_order}")
    agent.map_tools.draw_text_screen(.01, .03,
                                     "Task queue:\n{}".format(
                                         '\n'.join([str(task) for task in agent.task_manager.task_queue])))
    current_task_strings = sorted([str(task) for task in agent.task_manager.current_tasks])
    current_tasks_count = {s: current_task_strings.count(s) for s in current_task_strings}
    agent.map_tools.draw_text_screen(.5, .03,
                                     "Current tasks:\n{}".format(
                                         '\n'.join([f'{k} x{v}' for k, v in current_tasks_count.items()])))


def debug_units(agent: BasicAgent) -> None:
    """
    Displays unit information on screen:
        Unit type
        ID
        Current task
        Minerals left (for mineral fields)
    """
    for py_unit in agent.unit_collection.get_group(PLAYER_SELF):
        agent.map_tools.draw_text(py_unit.position, f"{py_unit.unit_type.name} ...{py_unit.id % 1000}\n"
                                                    f"{py_unit.task}")
        if py_unit.task.target_position:
            agent.map_tools.draw_line(py_unit.position, py_unit.task.target_position)
    for mineral in agent.unit_collection.get_group(PLAYER_NEUTRAL, lambda u: u.unit_type.is_mineral):
        agent.map_tools.draw_text(mineral.position, f"{mineral.unit_type.name} ...{mineral.id % 1000}\n"
                                                    f"Minerals left: {mineral.minerals_left_in_mineralfield}")


def up_up_down_down_left_right_left_right_b_a_start(agent: BasicAgent) -> None:
    """Gives resources and allows fast building, good for testing."""
    agent.debug_fast_build()
    agent.debug_give_all_resources()
    agent.debug_give_all_resources()
    agent.debug_give_all_resources()
    agent.debug_give_all_resources()
