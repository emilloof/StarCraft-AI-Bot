from math import sqrt
from modules.py_unit import PyUnit
from library import PLAYER_ENEMY, Point2D
from tasks.attack_scripts import AttackScripts
from library import PLAYER_ENEMY, Point2D, PLAYER_SELF
from modules.unit_collection import UnitCollection
import copy
# Function to calculate a distance between two Point2D.
scripts = ["kiting", "nok_av"]


def calculate_value(unit_list):
    total_value = 0
    if len(unit_list) > 0:
        for sim_unit in unit_list:
            if sim_unit.max_weapon_cooldown is not None and sim_unit.hp > 0: #Hittar inte felet ibland råkar det bli en NoneType
                total_value += (sqrt(sim_unit.hp) * (sim_unit.attack_damage / sim_unit.max_weapon_cooldown))
    return total_value


def value(situation):
    list1 = situation.U1
    list2 = situation.U2
    player1 = calculate_value(list1)
    player2 = calculate_value(list2)
    return player1 - player2


class Situation:
    def __init__(self, agent, unit=None, player=None, move=None):
        self.U1 = set()
        self.U2 = set()
        self.agent = agent
        self.time = agent.current_frame
        self.player = player
        self.script = move
        self.main_unit = unit
        self.main_unitx = None
        self.agent = agent
        self.add_units(agent)
        self.player = player

    def add_units(self, agent):
        self.U2.clear()
        self.U1.clear()
        for u in agent.unit_collection.get_group(PLAYER_SELF):
            if u.unit_type.is_combat_unit:
                new = UnitX(u)
                self.U1.add(new)
                if u == self.main_unit:
                    self.main_unitx = new
        for u in agent.unit_collection.get_group(PLAYER_ENEMY):
            if u.unit_type.is_combat_unit:
                self.U2.add(UnitX(u))


class UnitX:
    def __init__(self, py_unit):
        self.position = py_unit.position
        self.hp = py_unit.hp
        self.attack_range = py_unit.unit.unit_type.attack_range
        self.attack_damage = py_unit.unit.unit_type.attack_damage
        self.max_weapon_cooldown = py_unit.max_weapon_cooldown
        #self.unit = py_unit.unit



def ABCD(state, depth, alpha, beta, maxx, move=None):
    state.script = move

    if terminal(state, depth):
        return playout(state)

    if maxx:
        state.player = PLAYER_SELF
        best_value = -999999
        for script in scripts:
            best_value = max(best_value, ABCD(state, depth - 1, alpha, beta, False, script))
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break
        return best_value

    if not maxx:
        state.player = PLAYER_ENEMY
        best_value = 999999
        for script in scripts:
            best_value = min(best_value, ABCD(state, depth - 1, alpha, beta, True, script))
            beta = min(beta, best_value)
            if alpha >= beta:
                break
        return best_value


def alpha_beta_search(state, depth, maxx, move=None):
    if terminal(state, depth):
        return playout(state, move)

    if maxx:
        state.player = PLAYER_SELF
        best_value = float('-inf')  # Track the best value
        for script in scripts:
            tempvalue = alpha_beta_search(state, depth-1, False, script)
            best_value = max(best_value, tempvalue)
            if tempvalue >= best_value and depth != 3:  # Update state.script when finding a new best value
                state.script = script
        return best_value

    if not maxx:
        state.player = PLAYER_ENEMY
        best_value = float('inf')
        for script in scripts:
            tempvalue = alpha_beta_search(state, depth-1, True, script)
            best_value = min(best_value, tempvalue)
        return best_value



def playout(state, script):
    state.add_units(state.agent)
    AttackScripts.simulate(state, script)
    return value(state)


def terminal(state: Situation, depth: int):
    if (len(state.U2) != 0 and calculate_value(state.U2) == 0) or depth == 0:
        return True
    return False


