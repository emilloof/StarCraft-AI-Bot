from __future__ import annotations
from typing import TYPE_CHECKING
from library import PLAYER_ENEMY, Color

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent


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
