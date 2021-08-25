from typing import Union, Optional
from library import UNIT_TYPEID, UPGRADE_ID
from modules.extra import get_id
import re


class BuildOrder:
    """Class used to parse and store build orders"""

    def __init__(self, file_name: str, separators=None):
        if separators is None:
            # Separator "\t" is used by lotv.spawningtool.com
            separators = ["\t", ";"]
        self.order: list[Union[UNIT_TYPEID, UPGRADE_ID]] = self.parse(file_name, separators)

    def __repr__(self):
        return self.order.__repr__()

    @staticmethod
    def parse(file_name: str, separators: list[str]) -> list[Union[UNIT_TYPEID, UPGRADE_ID]]:
        """
        Parses a text file of the format used for build orders at https://lotv.spawningtool.com/build/
        The format is the following for each row in the file:
            <supply to build at><sep><units/upgrades to build><sep><comment>
        Units to build is a comma separated list where each item is of the form:
            <unit/upgrade name> (optional: x<ammount>)
        Example:
            42	Combat Shield, Refinery x2	This is a comment
        """
        order = []
        with open(file_name, "r") as f:
            for line in f:
                # Extract what to build, ignore digits (supply/timestamp)
                data = [item.strip() for item in re.split("|".join(separators), line) if
                        any(not s.strip().isdigit() for s in item.split(":"))]
                if not data or data[0] == "":
                    continue

                items = [(name, 1) for name in data[0].split(",")]
                for name, amount in items:
                    name = re.sub(r"\([^)]*\)", "", name).strip()  # Remove parentheses
                    last_word = name.split(" ")[-1]
                    if last_word.lower().startswith("x"):
                        # Build multiple
                        name = name.removesuffix(last_word)
                        amount = int(last_word[1:])
                    name = name.replace(' ', '').upper()
                    if name == "":
                        continue
                    name = BuildOrder.handle_edge_cases(name)
                    type_id = get_id(name)
                    if type_id is not None:
                        for i in range(amount):
                            order.append(type_id)
                    else:
                        print(f"BuildOrder: Could not parse type {name}")
        return order

    @staticmethod
    def handle_edge_cases(name: str) -> str:
        """
        Handles common edge cases, feel free to add more as you encounter them.
        :param name: Name of a unit/upgrade type.
        :return: Name corresponding to correct unit/upgrade in library.
        """
        if name == "TEMPLARARCHIVES":
            return "TEMPLARARCHIVE"
        if name == "VIKING":
            return "VIKINGFIGHTER"
        if "ARMORLEVEL" in name and "ARMORSLEVEL" not in name:
            return name.replace("ARMORLEVEL", "ARMORSLEVEL")
        return name

    def add(self, type_id: Union[UNIT_TYPEID, UPGRADE_ID]) -> None:
        """Adds a unit/upgrade type to the end of the build order"""
        self.order.append(type_id)

    def pop(self) -> Union[UNIT_TYPEID, UPGRADE_ID]:
        """Returns and removes the first item in the build order"""
        return self.order.pop(0)

    def peek(self) -> Optional[Union[UNIT_TYPEID, UPGRADE_ID]]:
        """Returns the first item in the build order without removing it"""
        if self.order:
            return self.order[0]
        return None

    def is_empty(self):
        return not bool(self.order)
