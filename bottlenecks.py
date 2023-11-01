from __future__ import annotations
from typing import TYPE_CHECKING
from library import Point2DI

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent

from library import PLAYER_SELF, PLAYER_NEUTRAL

def get_list_of_bottlenecks(agent: BasicAgent) -> dict:
    # Create map of each tile and associated depth
    depth_map = {}
    for x in range(agent.map_tools.width):
        for y in range(agent.map_tools.height):
            tile = Point2DI(x, y)
            depth_map[tile] = 0
    return depth_map


