from __future__ import annotations
from typing import TYPE_CHECKING
from library import Point2DI
import json

from modules.enemy_debugging import debug_enemies, debug_enemies_text
from modules.extra import get_neighbours
from modules.potential_flow.regions import (
    calculate_center,
    get_region,
    parse_regions,
    Region.get_tiles_as_tuples,
    regions_debug,
)

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent

from library import PLAYER_SELF, PLAYER_NEUTRAL


def print_depth(bottle_map: list, heat_map_row: list, x: int, y: int) -> bool:
    tile = Point2DI(x, y)
    if bottle_map[tile] == 1:
        heat_map_row.append(2)
        return True
    return False


mapd = dict()
on = False


def mother_debugger(agent: BasicAgent) -> None:
    # map = dict()
    # map.update(debug_terrain(agent))
    # map.update(debug_enemies(agent))
    global mapd
    global on
    # mapd.update(debug_enemies(agent))
    print(on)
    # if mapd:
    #    agent.debugger.set_display_values(mapd, (agent.map_tools.width, agent.map_tools.height))

    if on:
        agent.debugger.set_display_values(
            {(50, 50): 1}, (agent.map_tools.width, agent.map_tools.height)
        )
        on = not on
    else:
        on = not on
        agent.debugger.set_display_values(
            {(50, 50): 0}, (agent.map_tools.width, agent.map_tools.height)
        )


def debug_regions(agent: BasicAgent) -> None:
    regions = Region.get_tiles_as_tuples(agent.regions)
    rmap = regions_debug(regions)
    for region in regions:
        center = calculate_center(region[0])
        center = tuple(map(int, center))
        ic(center)
        rmap[center] = 15

    agent.debugger.set_display_values(
        rmap, (agent.map_tools.width, agent.map_tools.height)
    )


def debug_regions_old(agent: BasicAgent) -> None:
    # Opening JSON file

    rmap = dict()
    with open("points.json") as json_file:
        data = json.load(json_file)
        color = 1
        for region in data:
            for pos in data[region]:
                x = pos["x"]
                y = pos["y"]
                rmap[(int(x), int(y))] = color
            color += 1

    with open("centers.json") as json_file:
        data = json.load(json_file)
        color = 0
        for region in data:
            for center in data[region]:
                x = center["x"]
                y = center["y"]
                rmap[(int(x), int(y))] = color
            color += 1

    agent.debugger.set_display_values(
        rmap, (agent.map_tools.width, agent.map_tools.height)
    )


def debug_region_borders(agent: BasicAgent) -> None:
    regions = Region.get_tiles_as_tuples(agent.regions)
    rbmap = dict()
    color = 1
    for region in regions:
        for y in range(agent.map_tools.height):
            for x in range(agent.map_tools.width):
                if (x, y) not in region[0]:
                    for neighbour in get_neighbours(agent, (x, y)):
                        if neighbour in region[0]:
                            rbmap[neighbour] = color
        color += 1
    
    agent.debugger.set_display_values(rbmap, (agent.map_tools.width, agent.map_tools.height))

def debug_terrain(agent: BasicAgent) -> None:
    tmap = dict()
    for y in range(agent.map_tools.height):
        for x in range(agent.map_tools.width):
            if agent.map_tools.is_walkable(x, y):
                for neighbour in get_neighbours(agent, x, y).values():
                    if not agent.map_tools.is_walkable(neighbour[0], neighbour[1]):
                        tmap[neighbour] = 1
    print(tmap)
    agent.debugger.set_display_values(
        tmap, (agent.map_tools.width, agent.map_tools.height)
    )


def debug_map(agent: BasicAgent) -> None:
    """Displays the map in a separate window."""
    agent.debugger.set_display_values(path_debug(agent))


def debug_map(agent: BasicAgent, bottlenecks: dict) -> None:
    """Displays the map in a separate window."""
    heat_map = [
        [0 for _ in range(agent.map_tools.width)] for _ in range(agent.map_tools.height)
    ]
    for y in range(agent.map_tools.height):
        for x in range(agent.map_tools.width):
            if int(agent.map_tools.is_walkable(x, y)):
                b = False
                b = print_depth(
                    bottlenecks, heat_map[y], x, y
                )  # Avkommentera denna rad om du vill ha ursprungsfunktionaliteten (Används av eriei013)
                if not b:
                    heat_map[y][x] = 1

    agent.debugger.set_display_values(heat_map)

    # agent.debugger.set_display_values(path_debug(agent))


def path_debug(agent: BasicAgent) -> dict:
    """Displays the map in a separate window."""
    return {
        (x, y): int(agent.map_tools.is_walkable(x, y))
        for x in range(agent.map_tools.width)
        for y in range(agent.map_tools.height)
    }


def heat_map_debug(agent: BasicAgent) -> None:
    """Displays the map in a separate window."""
    heat_map = [
        [int(agent.map_tools.is_walkable(x, y)) for x in range(agent.map_tools.width)]
        for y in range(agent.map_tools.height)
    ]
    agent.debugger.set_display_values(heat_map)

def debug_region_text(agent: BasicAgent) -> None:
    """ Displays text on screen with information about which region the scout unit is in.
        Also illustrates the color of that region on the map."""
    for py_unit in agent.unit_collection.get_group(PLAYER_SELF):
        region = get_region(agent, agent.regions, py_unit.tile_position)
        agent.map_tools.draw_text(py_unit.position, f"Region: {region}")
        agent.map_tools.draw_text(py_unit.position, f"Region: {region}", color=(255, 0, 0))
        if region:
            agent.map_tools.draw_line(py_unit.position, region[1])

def debug_text(agent: BasicAgent) -> None:
    """Displays text on screen with information about build order and tasks."""
    agent.map_tools.draw_text_screen(0.01, 0.01, f"Build order: {agent.build_order}")
    agent.map_tools.draw_text_screen(
        0.01,
        0.03,
        "Task queue:\n{}".format(
            "\n".join([str(task) for task in agent.task_manager.task_queue])
        ),
    )
    current_task_strings = sorted(
        [str(task) for task in agent.task_manager.current_tasks]
    )
    current_tasks_count = {
        s: current_task_strings.count(s) for s in current_task_strings
    }
    agent.map_tools.draw_text_screen(
        0.5,
        0.03,
        "Current tasks:\n{}".format(
            "\n".join([f"{k} x{v}" for k, v in current_tasks_count.items()])
        ),
    )


def debug_units(agent: BasicAgent) -> None:
    """
    Displays unit information on screen:
        Unit type
        ID
        Current task
        Minerals left (for mineral fields)
    """
    for py_unit in agent.unit_collection.get_group(PLAYER_SELF):
        agent.map_tools.draw_text(
            py_unit.position,
            f"{py_unit.unit_type.name} ...{py_unit.id % 1000}\n" f"{py_unit.task}",
        )
        if py_unit.task.target_position:
            agent.map_tools.draw_line(py_unit.position, py_unit.task.target_position)
    for mineral in agent.unit_collection.get_group(
        PLAYER_NEUTRAL, lambda u: u.unit_type.is_mineral
    ):
        agent.map_tools.draw_text(
            mineral.position,
            f"{mineral.unit_type.name} ...{mineral.id % 1000}\n"
            f"Minerals left: {mineral.minerals_left_in_mineralfield}",
        )


def up_up_down_down_left_right_left_right_b_a_start(agent: BasicAgent) -> None:
    """Gives resources and allows fast building, good for testing."""
    agent.debug_fast_build()
    agent.debug_give_all_resources()
    agent.debug_give_all_resources()
    agent.debug_give_all_resources()
    agent.debug_give_all_resources()


def control_enemy(agent: BasicAgent) -> None:
    """Gives control of enemy units to the player."""
    agent.debug_enemy_control()
