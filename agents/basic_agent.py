from functools import cached_property
from typing import Union
import library as pycc

from config import DEBUG_CHEATS, DEBUG_CONSOLE, DEBUG_LOGS, DEBUG_TEXT, DEBUG_UNIT, DEBUG_VISUAL, FRAME_SKIP, \
    BUILD_ORDER_PATH, USE_CHOKES, DEBUG_ENEMIES, FRAME_CLEAR_CACHE, USE_MOVE, USE_PFSCOUT
from modules import BuildOrder, RegionManager, TaskManager, UnitCollection, PyBuildingPlacer, debugging as debug
from modules.extra import unit_types_by_condition
import bottlenecks as bottle    # Erik
from modules.path_finding import vertex #For pathfinding - hanlu520


# David
from strategy import Strategy

from icecream import install
install()

if DEBUG_VISUAL:
    from visualdebugger import HeatMapDebugger, PathDebugger

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

        # David
        self.hp_tracker = {}
        self.strategy = Strategy
        self.bayes_model = self.strategy.create_bayes_model(self)
        self.curr_strategy = {}
        self.curr_stratstr = ''
        self.last_hp_diff = 0

        # Vincent
        self.clear_cache_frame = 0
        self.region_manager: RegionManager = RegionManager(self)
        self.cache_functions: set[callable] = set()
        self.cache_manager: {module: {callable:{'last_clear': int, 'max_count': int}}} = dict()

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
            self.debugger: Union[HeatMapDebugger, PathDebugger] = HeatMapDebugger()

        if DEBUG_LOGS:
            self.timer = TicToc(prints=DEBUG_CONSOLE)
            self.logger = Logger()

    @cached_property
    def non_start_bases_positions(self) -> frozenset:
        return frozenset(base.position for base in self.base_location_manager.base_locations
                         if (not (base.is_player_start_location(pycc.PLAYER_SELF)
                                  or base.is_player_start_location(pycc.PLAYER_ENEMY))))

    @cached_property
    def vertex_dict(self):
        # Safe-path init for vertex with all neccessary vertex data
        vertex_dict = {}
        for y in range(self.map_tools.height):
            for x in range(self.map_tools.width):
                if (self.map_tools.is_walkable(x, y)):
                    current_point = (x, y)
                    vertex_dict[current_point] = (vertex.Vertex(current_point))
        return vertex_dict

    def on_game_start(self) -> None:
        """Runs on game start. Loads necessary data and generates settings"""
        pycc.IDABot.on_game_start(self)
        self.tech_tree.suppress_warnings(True)
        self.WORKER_TYPES = unit_types_by_condition(self, lambda u: u.is_worker)
        self.COMBAT_TYPES = unit_types_by_condition(self, lambda u: u.is_combat_unit)

        start_base_pos = self.base_location_manager.get_player_starting_base_location(
            pycc.PLAYER_SELF).position
        if USE_CHOKES:
            self.BOTTLENECKS = bottle.get_bottlenecks(self, start_base_pos)    # ERIk
        if USE_MOVE:
            # init vertex_dict
            _ = self.vertex_dict
        if USE_PFSCOUT:
            self.region_manager.on_start()
        if DEBUG_VISUAL:
            self.set_up_debugging()
            self.debugger.on_start()
            self.debugger.on_step(lambda: debug.debug_map(self))
        if DEBUG_CHEATS:
            debug.up_up_down_down_left_right_left_right_b_a_start(self)

    def on_step(self) -> None:
        """Runs on every step and runs IDABot.on_step.
        Updates variables, reassigns units, updates debug info."""

        pycc.IDABot.on_step(self)

        if self.current_frame % FRAME_SKIP == 1:
            if DEBUG_LOGS:
                self.logger.new_row()
                self.timer.tic()

            self.internal_gas = self.gas
            self.internal_minerals = self.minerals
            self.internal_supply = self.current_supply

            self.unit_collection.on_step()

            if USE_CHOKES:
                self.update_supply_depots()

        
        for bott in self.BOTTLENECKS: # ERIK
            for tile in bott:
                self.map_tools.draw_tile(tile, pycc.Color.BLUE)


        if self.current_frame % FRAME_SKIP == 1:
            new_units = [
                u for u in self.unit_collection.new_units_this_step if u.player == pycc.PLAYER_SELF
            ]
            self.task_manager.on_step(new_units)

            self.unit_collection.remove_dead_units()
        else:
            self.task_manager.on_step_every_frame()

        if self.current_frame % FRAME_SKIP == 1 and DEBUG_LOGS:
            self.timer.toc()
            self.logger.add("frame", self.current_frame)
            self.logger.add("units", len(self.unit_collection.get_group(pycc.PLAYER_SELF)))
            for key, val in self.timer:
                self.logger.add(key, val)
            self.timer.reset()

        # David
        # Only run the strategy decider every 100 tick
        # 675 tick equals roughly 30 sec
        if self.current_frame % 100 == 0:
            self.update_strategy()

        if DEBUG_UNIT:
            debug.debug_units(self)
        if DEBUG_TEXT:
            debug.debug_text(self)
        if DEBUG_ENEMIES:
            debug.debug_enemies(self)
            debug.debug_enemies_text(self)
        if DEBUG_VISUAL:
            self.debugger.on_step()
            self.map_tools.draw_text_screen(0.01, 0.01, f"frame: {self.current_frame}")

        if (self.current_frame - self.clear_cache_frame) % FRAME_CLEAR_CACHE == 1:
            self.clear_cache_functions()

    def update_strategy(self):
        # print("time: ", self.time)
        self.curr_strategy, self.curr_stratstr, self.hp_tracker, self.last_hp_diff = self.strategy.choose_strategy(
            self, self.strategy, self.bayes_model, self.hp_tracker,
            self.strategy.get_hit_points(self), self.internal_minerals, self.current_frame,
            self.last_hp_diff)
        # print(f'Current strategy: {self.curr_stratstr} \n Goal State: {self.curr_strategy}')
        # exit()

    def clear_cache_functions(self):
        self.clear_cache_frame = self.current_frame
        for func in self.cache_functions:
            if callable(func):    # hasattr(func, "cache_clear"):
                func.cache_clear()
            else:
                del func

    def update_supply_depots(self):
        if DEBUG_VISUAL:
            for bott in self.BOTTLENECKS:    # ERIK
                for tile in bott:
                    self.map_tools.draw_tile(tile, pycc.Color.BLUE)

        all_friendly = set(u for u in self.unit_collection.py_units.values()
                           if u.player == pycc.PLAYER_SELF)
        all_enemies = set(u for u in self.unit_collection.py_units.values()
                           if u.player == pycc.PLAYER_ENEMY)
        all_supply_depots = {
            py_unit
            for py_unit in all_friendly
            if py_unit.unit_type.unit_typeid == pycc.UNIT_TYPEID.TERRAN_SUPPLYDEPOT
            or py_unit.unit_type.unit_typeid == pycc.UNIT_TYPEID.TERRAN_SUPPLYDEPOTLOWERED
        }
      
        for supply_depot in all_supply_depots:
            is_enemy_unit_nearby = any(
                bottle.distance_between_tiles(supply_depot.tile_position, unit.tile_position) < 6
                for unit in all_enemies)
            if not is_enemy_unit_nearby:
                supply_depot.ability(pycc.ABILITY_ID.MORPH_SUPPLYDEPOT_LOWER)
            else:
                supply_depot.ability(pycc.ABILITY_ID.MORPH_SUPPLYDEPOT_RAISE)

    def set_up_debugging(self) -> None:
        """Set up visual debugger"""
        self.debugger.tile_margin = 1
        # sets the colormap for the debugger {(interval): (r, g, b)}
        color_map = {
            (0, 0): (0, 0, 0),
            (1, 1): (255, 255, 255),
            (2, 2): (0, 255, 0),
            (3, 3): (255, 0, 0),
            (4, 4): (0, 0, 255),
            (5, 5): (255, 255, 0),
            (6, 6): (255, 0, 255),
            (7, 7): (0, 255, 255),
            (8, 8): (100, 100, 0),
            (9, 9): (0, 100, 100),
            (10, 10): (100, 0, 100),
            (11, 11): (100, 100, 255),
            (12, 12): (100, 255, 100),
            (13, 13): (255, 100, 100),
            (14, 14): (255, 150, 100),
            (15, 15): (100, 100, 100)
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
