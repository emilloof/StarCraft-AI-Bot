from modules.unit_collection import UnitCollection
from modules.py_unit import PyUnit
from library import PLAYER_SELF, PLAYER_ENEMY, PLAYER_NEUTRAL, UNIT_TYPEID, Unit
from pgmpy.models import  BayesianNetwork
from pgmpy.factors.discrete import TabularCPD


 # Lists the units that are classified as offensive
OFFENSIVE_UNITS = ['TERRAN_MARINE', 'TERRAN_MARAUDER', 'TERRAN_REAPER', 'TERRAN_HELLION', 
                   'TERRAN_HELLBAT', 'TERRAN_WIDOWMINE', 'TERRAN_SIEGETANK', 'TERRAN_CYCLONE', 
                   'TERRAN_THOR', 'TERRAN_BANSHEE', 'TERRAN_BATTLECRUISER']
# Least amount of offensive unit we want to have to choose an offensive strategy
LIMIT_OFF_UNITS = 25


class Strategy:

    
    def __init__(self) -> None:
        self.unit_collecition = UnitCollection
        self.py_unit = PyUnit
        self.unit = Unit
       

       
        
       
    
    def print_unit_collection(self):
        
        unit_dict = {}
        for pyunit in self.unit_collection.get_group():
            if pyunit.unit_type.name in unit_dict.keys():
                unit_dict[pyunit.unit_type.name] += 1
            else:
                unit_dict[pyunit.unit_type.name] = 1

        
        print(unit_dict)

    def create_bayes_model(self) -> BayesianNetwork:
        strategy_model = BayesianNetwork(
            [
                 ("> 25 offensive units", "Offensive"),
                 ("Building lost defence", "Offensive"),
                 ("> x amount of minerals", "Offensive"),
                 ("> 25 offensive units", "Defensive"),
                 ("Building lost defence", "Defensive"),
                 ("> x amount of minerals", "Defensive"),
                 ("> 25 offensive units", "Expansive"),
                 ("Building lost defence", "Expansive"),
                 ("> x amount of minerals", "Expansive"),
            ]
        )
        cpd_over_25_offensive_units = TabularCPD(variable="> 25 offensive units", variable_card=2, values=[[0.5], [0.5]])
        cpd_building_lost_defence = TabularCPD(variable="Building lost defence", variable_card=2, values=[[0.5], [0.5]])
        cpd_over_x_amount_of_minerals = TabularCPD(variable="> x amount of minerals", variable_card=2, values=[[0.5], [0.5]])
        cpd_offensive = TabularCPD(
            variable="Offensive",
            variable_card=2,
            values=[
                # 0    1    2    3    4    5    6    7
                #000  001  010  011  100  101  110  111  
                [0.9, 0.9, 0.1, 0.1, 0.9, 0.9, 0.5, 0.5], # Offensive = False [0]
                [0.1, 0.1, 0.9, 0.9, 0.1, 0.1, 0.5, 0.5] # Offensive = True [1]
                    ],
            evidence=["Building lost defence", "> 25 offensive units", "> x amount of minerals"],
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
            evidence=["Building lost defence", "> 25 offensive units", "> x amount of minerals"],
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
            evidence=["Building lost defence", "> 25 offensive units", "> x amount of minerals"],
            evidence_card=[2, 2, 2],
        )
        
        # Associating the parameters with the model structure and checking if they are valid
        strategy_model.add_cpds(cpd_over_25_offensive_units, cpd_building_lost_defence, cpd_over_x_amount_of_minerals, cpd_offensive, cpd_defensive, cpd_expansive)
        strategy_model.check_model()
        print("Nodes in the model: ", strategy_model.nodes())
        print("Edges in the model: ", strategy_model.edges())

        return strategy_model
    
        
    def get_number_offensive_units(self, player=PLAYER_SELF) -> int:
        units = 0
        for pyunit in self.unit_collection.get_group(player):
            if pyunit.unit_type.name in OFFENSIVE_UNITS:
                units += 1

        return units
    
    def get_hit_points(self):
        hit_points = 0
        for pyunit in self.unit_collection.get_group(PLAYER_SELF):
            print(f'UnitType: {pyunit.unit_type.name}, HP: {pyunit.get_hp()}')
        return hit_points
    
 
        