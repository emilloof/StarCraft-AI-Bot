from __future__ import annotations

from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent

from modules.extra import get_enemies_in_radius
from tasks.pf_scout import PFscout
from tasks.scout import Scout

class ScoutTester:
    def __init__(self, agent: BasicAgent):
        self.enemies = {}
        self.agent = agent
        self.scout: Union[PFscout, Scout] = None
        self.scout_units = {}
    
    def serialize_enemies(self):
        return [(str(unit.unit_type.unit_typeid).split(".")[1], count) for unit, count in self.enemies.items()]
    
    def serialize_scout_units(self):
        return [count for unit, count in self.scout_units.items() if not unit.is_alive]

    def on_step(self):
        if self.scout is None:
            return
        scout_unit = None
        if isinstance(self.scout, PFscout):
            scout_unit = self.agent.latest_pfscout_unit
        elif isinstance(self.scout, Scout):
            scout_unit = self.agent.latest_scout_unit
        
        if scout_unit in self.scout_units:
            self.scout_units[scout_unit] += 1
        else:
            self.scout_units[scout_unit] = 1

        new_enemies = get_enemies_in_radius(self.agent, scout_unit.position, scout_unit.unit_type.sight_range)

        for enemy in new_enemies:
            if enemy.unit in self.enemies:
                self.enemies[enemy.unit] += 1
            else:
                self.enemies[enemy.unit] = 1
