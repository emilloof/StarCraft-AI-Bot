from modules.unit_collection import UnitCollection
from modules.py_unit import PyUnit
from library import PLAYER_SELF, Unit, UPGRADE_ID
from pgmpy.models import  BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from config import DEBUG_BAYESIAN




 # Lists the units that are classified as offensive
OFFENSIVE_UNITS = ['TERRAN_MARINE', 'TERRAN_MARAUDER', 'TERRAN_REAPER', 'TERRAN_HELLION', 
                   'TERRAN_HELLBAT', 'TERRAN_WIDOWMINE', 'TERRAN_SIEGETANK', 'TERRAN_CYCLONE', 
                   'TERRAN_THOR', 'TERRAN_BANSHEE', 'TERRAN_BATTLECRUISER']
STRUCTURES = ['TERRAN_ARMORY', 'TERRAN_BARRACKS', 'TERRAN_BUNKER', 'TERRAN_COMMANDCENTER', 
              'TERRAN_ORBITALCOMMAND', 'TERRAN_PLANETARYFORTRESS', 'TERRAN_ENGINEERINGBAY', 
              'TERRAN_FACTORY', 'TERRAN_FUSIONCORE', 'TERRAN_GHOSTACADEMY', 'TERRAN_MISSILETURRET', 
              'TERRAN_REFINERY', 'TERRAN_SENSORTOWER', 'TERRAN_STARPORT', 'TERRAN_SUPPLYDEPOT']
# Least amount of offensive unit we want to have to choose an offensive strategy
LIMIT_OFF_UNITS = 25

# Upgrades for different strategys
UPGRADES = {'Offensive': [UPGRADE_ID.MARINESTIMPACK, UPGRADE_ID.REAPERSTIMPACK, UPGRADE_ID.COMBATSHIELD, UPGRADE_ID.SIEGETECH, UPGRADE_ID.MULE],
            'Defensive': [UPGRADE_ID.TERRANBUILDINGARMOR, UPGRADE_ID.TERRANINFANTRYARMORSLEVEL1, UPGRADE_ID.TERRANINFANTRYARMORSLEVEL2, UPGRADE_ID.TERRANINFANTRYARMORSLEVEL3,
                          UPGRADE_ID.TERRANINFANTRYWEAPONSLEVEL1, UPGRADE_ID.TERRANINFANTRYWEAPONSLEVEL2, UPGRADE_ID.TERRANINFANTRYWEAPONSLEVEL3, UPGRADE_ID.MULE],
            'Expansive': [UPGRADE_ID.MULE, UPGRADE_ID.TERRANBUILDINGARMOR]}

# Define what units and structures a certain strategy should produce
STRATEGYS = {'Offensive': {'TERRAN_MARINE': 8, 'TERRAN_REAPER': 5, 'TERRAN_HELLION': 2, 'upgrades': UPGRADES['Offensive']},
             "Defensive": {'TERRAN_SIEGETANK': 2, 'TERRAN_HELLION': 2, 'TERRAN_WIDOWMINE': 2, 'TERRAN_CYCLONE': 2, 'TERRAN_BUNKER': 2, 'TERRAN_SENSORTOWER': 1, 'upgrades': UPGRADES['Defensive']},
             'Expansive': {'TERRAN_COMMANDCENTER': 1, 'TERRAN_SUPPLYDEPOT': 1, 'TERRAN_BARRACKS': 1, 'TERRAN_FACTORY': 1,'TERRAN_SENSORTOWER': 1, 'upgrades': UPGRADES['Expansive']}}

class Strategy:
    
    def __init__(self) -> None:
        self.unit_collecition = UnitCollection
        self.py_unit = PyUnit
        self.unit = Unit
       

    def print_unit_collection(self):
        """ Testing function..."""
        unit_dict = {}
        for pyunit in self.unit_collection.get_group():
            if pyunit.unit_type.name in unit_dict.keys():
                unit_dict[pyunit.unit_type.name] += 1
            else:
                unit_dict[pyunit.unit_type.name] = 1

        
        print(unit_dict)

    def create_bayes_model(self) -> BayesianNetwork:
        """ Creates and returns a Bayesian network"""
        strategy_model = BayesianNetwork(
            [
                 ("Gametime < 2700 tick", "Offensive"),
                 ("Enemy attack last 675 tick", "Enemy offensive"),
                 ("Enemy offensive", "Offensive"),
                 ("Building lost defence", "Defensive"),
                 ("Many minerals", "Defensive"),
                 ("Enemy offensive", "Expansive"),
                 ("Building lost defence", "Expansive"),
                 ("Many minerals", "Expansive"),
            ]
        )

        cpd_gametime_under_2700_tick = TabularCPD(variable="Gametime < 2700 tick", variable_card=2, values=[[0.5], [0.5]])
        cpd_building_lost_defence = TabularCPD(variable="Building lost defence", variable_card=2, values=[[0.5], [0.5]])
        cpd_many_minerals = TabularCPD(variable="Many minerals", variable_card=2, values=[[0.5], [0.5]])
        cpd_enemy_attack_last_675_tick = TabularCPD(variable="Enemy attack last 675 tick", variable_card=2, values=[[0.5], [0.5]])


        cpd_enemy_offensive = TabularCPD(
             variable="Enemy offensive",
             variable_card=2, 
             values=[
                  # 0   1
                  [0.9, 0.1], # Enemy offensive = False [0]
                  [0.1, 0.9] # Enemy offensive = True [1]
             ],
             evidence=["Enemy attack last 675 tick"],
             evidence_card=[2]
        )

        cpd_offensive = TabularCPD(
            variable="Offensive",
            variable_card=2,
            values=[
                # 0    1    2    3
                # 00   01   10   11  
                [0.5, 0.8, 0.0, 0.0], # Offensive = False [0]
                [0.5, 0.2, 1.0, 1.0] # Offensive = True [1]
                    ],
            evidence=["Gametime < 2700 tick", "Enemy offensive"],
            evidence_card=[2, 2],
        )
        cpd_defensive = TabularCPD(
            variable="Defensive",
            variable_card=2,
            values=[
                # 0    1    2    3
                # 00   01   10  11 
                [0.9, 0.9, 0.2, 0.2], # Defensive = False [0]
                [0.1, 0.1, 0.8, 0.8] # Defensive = True [1]
                    ],
            evidence=["Building lost defence", "Many minerals"],
            evidence_card=[2, 2],
        )
        cpd_expansive = TabularCPD(
            variable="Expansive",
            variable_card=2,
            values=[
                # 0    1    2    3    4    5    6    7
                #000  001  010  011  100  101  110  111 
                [0.9, 1.0, 0.1, 0.3, 0.9, 1.0, 0.5, 0.7], # Expansive = False [0]
                [0.1, 0.0, 0.9, 0.7, 0.1, 0.0, 0.5, 0.3] # Expansive = True [1]
                    ],
            evidence=["Building lost defence", "Many minerals", "Enemy offensive"],
            evidence_card=[2, 2, 2],
        )
        
        # Associating the parameters with the model structure and checking if they are valid
        strategy_model.add_cpds(cpd_gametime_under_2700_tick, cpd_building_lost_defence, cpd_many_minerals, cpd_enemy_offensive, 
                                cpd_offensive, cpd_defensive, cpd_expansive, cpd_enemy_attack_last_675_tick)
        strategy_model.check_model()

        if DEBUG_BAYESIAN:
            print("Bayes model OK")
            print("Nodes in the model: ", strategy_model.nodes())
            print("Edges in the model: ", strategy_model.edges())

        return strategy_model
    
    
    def choose_strategy(self, strategy,  strategy_model: BayesianNetwork, hp_tracker: dict, updated_hp_tracker: dict, minerals: int, time: int, last_hp_diff: int ) -> (dict, dict, int):
        """ Returns the best strategy aswell as an updated dict of the hp for our strucutres"""

        enemy_attack_last_675_tick = 0
        building_lost_def = strategy.check_building_diff(self, hp_tracker, updated_hp_tracker)
        if building_lost_def == 1:
             last_hp_diff = time
             enemy_attack_last_675_tick = 1
        if (time > 675 or last_hp_diff != 0) and time - last_hp_diff < 675:
             enemy_attack_last_675_tick = 1
        many_minerals = strategy.many_minerals(self, minerals)

        over_25_off_units = strategy.is_over_25_off_units(self)
        
        
        #check_minerals = lambda miner, x: 1 if miner > x else 0
        #over_400_minerals = check_minerals(minerals, 400)
        #print(over_400_minerals)
        check_gametime = lambda time_, y: 1 if time_ < y else 0
        under_2700_tick = check_gametime(time, 2700)
 
        evidence = {"Building lost defence": building_lost_def, "Gametime < 2700 tick": under_2700_tick, 
                    "Many minerals": many_minerals, "Enemy attack last 675 tick": enemy_attack_last_675_tick}

        inference = VariableElimination(strategy_model)
        prob_exp = inference.query(variables=["Expansive"], evidence=evidence)
        prob_off = inference.query(variables=["Offensive"], evidence=evidence)
        prob_def =  inference.query(variables=["Defensive"], evidence=evidence)
        best_strat = strategy.decide_strat([prob_exp, prob_off, prob_def]) 


        return STRATEGYS[best_strat], best_strat, updated_hp_tracker, last_hp_diff
    
    def decide_strat(strats: list) -> dict:
        """ Takes in arguments as probabilities for a certain strategy and returns the best based on the probs"""
        # best_strat[0] is hte name of the strategy
        # best_strat[1] is the value given from the bayes network
        best_strat = ['', 0]
        for strat in strats:
            if DEBUG_BAYESIAN:
                print(strat.variables[0], " ", strat.values[1])
            if strat.values[1] > best_strat[1]:
                best_strat[0] = strat.variables[0]
                # Truth value
                best_strat[1] = strat.values[1]
            elif strat.values[1] == best_strat[1]:
                 best_strat[0] += strat.variables[0]

        return best_strat[0]

         
    

    def check_building_diff(self, hp_tracker: dict, updated_hp_tracker: dict) -> int:
        """ Returns 1 if any building has lost hp since last check, else return 0 """
        if hp_tracker != updated_hp_tracker:
            for pyunit in self.unit_collection.get_group(PLAYER_SELF):
                
                if pyunit.unit_type.name in STRUCTURES and \
                    pyunit.id in updated_hp_tracker and \
                        pyunit.id in hp_tracker and \
                            updated_hp_tracker[pyunit.id] < hp_tracker[pyunit.id]:
                                return 1
        return 0


    def get_hit_points(self) -> dict:
        """ Returns the hp of all of our structures"""
        hp_tracker = {}
        for pyunit in self.unit_collection.get_group(PLAYER_SELF):
            if pyunit.unit_type.name in STRUCTURES:
                hp_tracker[pyunit.id] = pyunit.get_hp()
        return hp_tracker
    
        
    def is_over_25_off_units(self) -> int:
        """ Returns 1 if we have over 25 offensive units, else 0 """
        units = 0
        for pyunit in self.unit_collection.get_group(PLAYER_SELF):
            #print(pyunit.unit_type.unit_typeid)
            #exit()
            if pyunit.unit_type.name in OFFENSIVE_UNITS:
                if DEBUG_BAYESIAN:
                    print(pyunit.unit_type.unit_typeid)
                    print(UPGRADE_ID.MARINESTIMPACK)
                units += 1
        if units > 25:
            return 1
        return 0
    

    def many_minerals(self, minerals: int) -> int:
        bases = 0
        for pyunit in self.unit_collection.get_group(PLAYER_SELF):
            if pyunit.unit_type.name == 'TERRAN_COMMANDCENTER':
                bases += 1
        if bases == 0:
             return 0
        if (minerals / bases**2) > 500:
             return 1
        return 0
    
    
    
    
    


        
        