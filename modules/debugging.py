from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent

from library import PLAYER_SELF, PLAYER_NEUTRAL


def debug_map(agent: BasicAgent) -> None:
    """Displays the map in a separate window."""
    heat_map = [[int(agent.map_tools.is_walkable(x, y)) for x in range(agent.map_tools.width)]
                for y in range(agent.map_tools.height)]
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
