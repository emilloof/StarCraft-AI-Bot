from modules.unit_collection import UnitCollection
from modules.py_unit import PyUnit
from library import PLAYER_SELF, PLAYER_ENEMY, PLAYER_NEUTRAL, UNIT_TYPEID, Unit
from pgmpy.models import  BayesianNetwork
from pgmpy.factors.discrete import TabularCPD


class Strategy:
    def __init__(self) -> None:
        self.unit_collecition = UnitCollection
        self.py_unit = PyUnit
        G = BayesianNetwork()
       
    
    def print_unit_collection(self):
        
        unit_dict = {}
        for pyunit in self.unit_collection.get_group(PLAYER_ENEMY):
            if pyunit.unit_type.name in unit_dict.keys():
                unit_dict[pyunit.unit_type.name] += 1
            else:
                unit_dict[pyunit.unit_type.name] = 1

        
        print(unit_dict)

    def create_bayes_model(self):
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
        