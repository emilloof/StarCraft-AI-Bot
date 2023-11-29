from modules.unit_collection import UnitCollection
from modules.py_unit import PyUnit
from library import PLAYER_SELF, PLAYER_ENEMY, PLAYER_NEUTRAL, UNIT_TYPEID, Unit
from pgmpy.models import  BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination




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
                 ("> 25 offensive units", "Offensive"),
                 ("Building lost defence", "Offensive"),
                 ("> 400 minerals", "Offensive"),
                 ("> 25 offensive units", "Defensive"),
                 ("Building lost defence", "Defensive"),
                 ("> 400 minerals", "Defensive"),
                 ("> 25 offensive units", "Expansive"),
                 ("Building lost defence", "Expansive"),
                 ("> 400 minerals", "Expansive"),
            ]
        )
        cpd_over_25_offensive_units = TabularCPD(variable="> 25 offensive units", variable_card=2, values=[[0.5], [0.5]])
        cpd_building_lost_defence = TabularCPD(variable="Building lost defence", variable_card=2, values=[[0.5], [0.5]])
        cpd_over_x_amount_of_minerals = TabularCPD(variable="> 400 minerals", variable_card=2, values=[[0.5], [0.5]])
        cpd_offensive = TabularCPD(
            variable="Offensive",
            variable_card=2,
            values=[
                # 0    1    2    3    4    5    6    7
                #000  001  010  011  100  101  110  111  
                [0.9, 0.9, 0.1, 0.1, 0.9, 0.9, 0.5, 0.5], # Offensive = False [0]
                [0.1, 0.1, 0.9, 0.9, 0.1, 0.1, 0.5, 0.5] # Offensive = True [1]
                    ],
            evidence=["Building lost defence", "> 25 offensive units", "> 400 minerals"],
            evidence_card=[2, 2, 2],
        )
        cpd_defensive = TabularCPD(
            variable="Defensive",
            variable_card=2,
            values=[
                # 0    1    2    3    4    5    6    7
                #000  001  010  011  100  101  110  111 
                [0.9, 0.9, 0.9, 0.9, 0.1, 0.1, 0.2, 0.2], # Defensive = False [0]
                [0.1, 0.1, 0.1, 0.1, 0.9, 0.9, 0.8, 0.8] # Defensive = True [1]
                    ],
            evidence=["Building lost defence", "> 25 offensive units", "> 400 minerals"],
            evidence_card=[2, 2, 2],
        )
        cpd_expansive = TabularCPD(
            variable="Expansive",
            variable_card=2,
            values=[
                # 0    1    2    3    4    5    6    7
                #000  001  010  011  100  101  110  111 
                [0.9, 0.1, 0.9, 0.1, 0.9, 0.5, 0.9, 0.5], # Expansive = False [0]
                [0.1, 0.9, 0.1, 0.9, 0.1, 0.5, 0.1, 0.5] # Expansive = True [1]
                    ],
            evidence=["Building lost defence", "> 25 offensive units", "> 400 minerals"],
            evidence_card=[2, 2, 2],
        )
        
        # Associating the parameters with the model structure and checking if they are valid
        strategy_model.add_cpds(cpd_over_25_offensive_units, cpd_building_lost_defence, cpd_over_x_amount_of_minerals, cpd_offensive, cpd_defensive, cpd_expansive)
        strategy_model.check_model()
        print("Nodes in the model: ", strategy_model.nodes())
        print("Edges in the model: ", strategy_model.edges())

        return strategy_model
    
    
    def choose_strategy(self, strategy,  strategy_model: BayesianNetwork, hp_tracker: dict, updated_hp_tracker: dict, minerals: int ) -> (str, dict):
        """ Returns the best strategy aswell as an updated dict of the hp for our strucutres"""

        building_lost_def = strategy.check_building_diff(self, hp_tracker, updated_hp_tracker)
        over_25_off_units = strategy.is_over_25_off_units(self)
        check_minerals = lambda miner, x: 1 if miner > x else 0
        over_400_minerals = check_minerals(minerals, 400)
        print(over_400_minerals)
        evidence = {"Building lost defence": building_lost_def, "> 25 offensive units": over_25_off_units, "> 400 minerals": over_400_minerals}

        inference = VariableElimination(strategy_model)
        prob_exp = inference.query(variables=["Expansive"], evidence=evidence)
        prob_off = inference.query(variables=["Offensive"], evidence=evidence)
        prob_def =  inference.query(variables=["Defensive"], evidence=evidence)


        return strategy.decide_strat([prob_exp, prob_off, prob_def]), updated_hp_tracker
    
    def decide_strat(strats: list) -> str:
        """ Takes in arguments as probabilities for a certain strategy and returns the best based on the probs"""
        # best_strat[0] is hte name of the strategy
        # best_strat[1] is the value given from the bayes network
        best_strat = ['', 0]
        for strat in strats:
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
            if pyunit.unit_type.name in OFFENSIVE_UNITS:
                units += 1
        if units > 25:
            return 1
        return 0
    
    
    
    
    


        
        