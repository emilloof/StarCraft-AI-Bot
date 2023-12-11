from __future__ import annotations
from typing import TYPE_CHECKING

from modules.potential_flow.regions import (
    Region,
    regions_debug,
)

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent

from library import PLAYER_SELF, PLAYER_NEUTRAL, PLAYER_ENEMY, Color, Point2DI

# Skapad av eriei013 för testning
def print_depth(bottle_map: dict, heat_map_row: list, x: int, y: int) -> bool:
    tile = Point2DI(x, y)
    if bottle_map[tile] == 1:
        heat_map_row.append(2)
        return True
    return False


def debug_regions(agent: BasicAgent) -> None:
    regions: set[Region] = {region.tiles_as_tuples for region in agent.regions}
    rmap = regions_debug(regions)
    for region in regions:
        center = calc_center(region[0])
        center = tuple(map(int, center))
        # ic(center)
        rmap[center] = 15

    agent.debugger.set_display_values(
        rmap, (agent.map_tools.width, agent.map_tools.height)
    )


def debug_region_borders(agent: BasicAgent) -> None:
    rbmap = {}
    for color, region in enumerate(agent.regions, start=1):
        for border_tile in region.get_border():
            rbmap[(border_tile.x, border_tile.y)] = color
    agent.debugger.set_display_values(rbmap, (agent.map_tools.width, agent.map_tools.height))


def debug_terrain(agent: BasicAgent) -> None:
    tmap = {}
    for y in range(agent.map_tools.height):
        for x in range(agent.map_tools.width):
            if agent.map_tools.is_walkable(x, y):
                for neighbour in get_neighbours2(agent, x, y).values():
                    if not agent.map_tools.is_walkable(neighbour[0], neighbour[1]):
                        tmap[neighbour] = 1
    agent.debugger.set_display_values(tmap, (agent.map_tools.width, agent.map_tools.height))


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


def debug_text(agent: ImprovedAgent) -> None:
    """Displays text on screen with information about build order and tasks."""
    agent.map_tools.draw_text_screen(0.01, 0.01, f"Build order: {agent.build_order}")
    agent.map_tools.draw_text_screen(0.01, 0.03, "Task queue:\n{}".format(
        "\n".join([str(task) for task in agent.task_manager.task_queue])),)
    current_task_strings = sorted([str(task) for task in agent.task_manager.current_tasks])
    current_tasks_count = {s: current_task_strings.count(s) for s in current_task_strings}
    agent.map_tools.draw_text_screen(0.5, 0.03, "Current tasks:\n{}".format(
        "\n".join([f"{k} x{v}" for k, v in current_tasks_count.items()])),)


def debug_units(agent: ImprovedAgent) -> None:
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
            f"{py_unit.unit_type.name} ...{py_unit.id % 1000}\n"
            f"{py_unit.task}",
        )
        if py_unit.task.target_position:
            agent.map_tools.draw_line(py_unit.position, py_unit.task.target_position)
    for mineral in agent.unit_collection.get_group(
            PLAYER_NEUTRAL, lambda u: u.unit_type.is_mineral):
        agent.map_tools.draw_text(
            mineral.position, f"{mineral.unit_type.name} ...{mineral.id % 1000}\n"
            f"Minerals left: {mineral.minerals_left_in_mineralfield}",)


def up_up_down_down_left_right_left_right_b_a_start(agent: ImprovedAgent) -> None:
    """Gives resources and allows fast building, good for testing."""
    agent.debug_fast_build()
    agent.debug_give_all_resources()
    agent.debug_give_all_resources()
    agent.debug_give_all_resources()
    agent.debug_give_all_resources()

# ----------------- ENEMIES ----------------- #


def debug_enemies(agent: BasicAgent) -> None:
    """Draws a circle around known enemies"""
    for enemy in agent.unit_collection.get_group(PLAYER_ENEMY):
        agent.map_tools.draw_circle(enemy.position, 3, Color.RED)


def debug_enemies_map(agent: BasicAgent) -> None:
    """Displays the known enemies"""
    return {
        enemy.position: 2 for enemy in agent.unit_collection.get_group(PLAYER_ENEMY)
    }


def debug_enemies_text(agent: BasicAgent) -> None:
    """Displays the known enemies"""
    agent.map_tools.draw_text_screen(
        0.01,
        0.03,
        "Enemies:\n{}".format(
            "\n".join(
                [str(enemy) for enemy in agent.unit_collection.get_group(PLAYER_ENEMY)]
            )
        ),
    )
