from typing import Union
import library as pycc
from modules.build_order import BuildOrder
from modules.task_manager import TaskManager
from modules.unit_collection import UnitCollection
from modules.py_building_placer import PyBuildingPlacer
from modules import debugging as debug
from config import DEBUG_CHEATS, DEBUG_CONSOLE, DEBUG_LOGS, DEBUG_TEXT, DEBUG_UNIT, DEBUG_VISUAL, FRAME_SKIP, \
    BUILD_ORDER_PATH
from modules.extra import unit_types_by_condition

if DEBUG_VISUAL:
    from visualdebugger.heat_map_debugger import HeatMapDebugger

if DEBUG_LOGS:
    from modules.tictoc import TicToc
    from modules.logger import Logger


class BasicAgent(pycc.IDABot):
    """Base agent for PyCommandCenter and SC2"""

    def __init__(self):
        pycc.IDABot.__init__(self)
        self.unit_collection = UnitCollection(self)
        self.build_order = BuildOrder(BUILD_ORDER_PATH)
        self.task_manager = TaskManager(self)
        self.py_building_placer = PyBuildingPlacer(self)
        self.internal_gas = 0
        self.internal_minerals = 0
        self.internal_supply = 0

        # Hard coded costs for upgrades since they are not available in the API
        self.UPGRADES = {
            pycc.UNIT_TYPEID.TERRAN_ORBITALCOMMAND: (150, 0),
            pycc.UNIT_TYPEID.TERRAN_PLANETARYFORTRESS: (150, 150),
            pycc.UNIT_TYPEID.ZERG_LAIR: (150, 100),
            pycc.UNIT_TYPEID.ZERG_HIVE: (200, 150)
        }
        self.WORKER_TYPES = set()
        self.COMBAT_TYPES = set()

        if DEBUG_VISUAL:
            self.debugger = HeatMapDebugger()

        if DEBUG_LOGS:
            self.timer = TicToc(prints=DEBUG_CONSOLE)
            self.logger = Logger()

    def on_game_start(self) -> None:
        """Runs on game start. Loads necessary data and generates settings"""
        pycc.IDABot.on_game_start(self)
        self.tech_tree.suppress_warnings(True)
        self.WORKER_TYPES = unit_types_by_condition(self, lambda u: u.is_worker)
        self.COMBAT_TYPES = unit_types_by_condition(self, lambda u: u.is_combat_unit)
        if DEBUG_VISUAL:
            self.set_up_debugging()
            self.debugger.on_start()
            self.debugger.on_step(lambda: debug.debug_map(self))
        if DEBUG_CHEATS:
            debug.up_up_down_down_left_right_left_right_b_a_start(self)

    def on_step(self) -> None:
        """Runs on every step and runs IDABot.on_step. Updates variables, reassigns units, updates debug info."""
        pycc.IDABot.on_step(self)

        if self.current_frame % FRAME_SKIP == 1:
            if DEBUG_LOGS:
                self.logger.new_row()
                self.timer.tic()

            self.internal_gas = self.gas
            self.internal_minerals = self.minerals
            self.internal_supply = self.current_supply

            self.unit_collection.on_step()

        if self.current_frame % FRAME_SKIP == 1:
            new_units = [u for u in self.unit_collection.new_units_this_step if u.player == pycc.PLAYER_SELF]
            self.task_manager.on_step(new_units)

            self.unit_collection.remove_dead_units()

        if self.current_frame % FRAME_SKIP == 1 and DEBUG_LOGS:
            self.timer.toc()
            self.logger.add("frame", self.current_frame)
            self.logger.add("units", len(self.unit_collection.get_group(pycc.PLAYER_SELF)))
            for key, val in self.timer:
                self.logger.add(key, val)
            self.timer.reset()

        if DEBUG_UNIT:
            debug.debug_units(self)
        if DEBUG_TEXT:
            debug.debug_text(self)

    def set_up_debugging(self) -> None:
        """Set up visual debugger"""
        self.debugger.tile_margin = 1
        # sets the colormap for the debugger {(interval): (r, g, b)}
        color_map = {
            (0, 0): (0, 0, 0,),
            (1, 1): (255, 255, 255)
        }
        self.debugger.set_color_map(color_map)

    def can_afford(self, unit_type: Union[pycc.UnitType, pycc.UPGRADE_ID]) -> bool:
        """
        Returns whether the agent have the sufficient minerals, vespene gas, and available supply to build
        unit/upgrade
        """
        minerals, gas, supply = self._cost(unit_type)
        supply_left = self.max_supply - self.internal_supply
        return self.internal_minerals >= minerals and self.internal_gas >= gas and supply_left >= supply

    def pay(self, unit_type: Union[pycc.UnitType, pycc.UPGRADE_ID]) -> None:
        """Reduces our internal resources as if the agent payed for the unit/upgrade"""
        minerals, gas, supply = self._cost(unit_type)
        self.internal_gas -= minerals
        self.internal_minerals -= gas
        self.internal_supply += supply

    def _cost(self, unit_type: Union[pycc.UnitType, pycc.UPGRADE_ID]) -> tuple[int, int, int]:
        """Calculates the mineral, gas, and supply cost of a unit/upgrade"""
        data = self.tech_tree.get_data(unit_type)
        minerals, gas, supply = data.mineral_cost, data.gas_cost, data.supply_cost
        if isinstance(unit_type, pycc.UnitType) and unit_type.unit_typeid in self.UPGRADES:
            minerals, gas = self.UPGRADES[unit_type.unit_typeid]
        return minerals, gas, supply
