from modules.unit_collection import UnitCollection
from modules.py_unit import PyUnit


class Strategy:
    def __init__(self) -> None:
        self.unit_collecition = UnitCollection
        self.py_unit = PyUnit
       
    
    def print_unit_collection(self):
        
        unit_dict = {}
        for pyunit in self.unit_collection.get_group():
            if pyunit.unit_type.name in unit_dict.keys():
                unit_dict[pyunit.unit_type.name] += 1
            else:
                unit_dict[pyunit.unit_type.name] = 1

        
        print(unit_dict)


