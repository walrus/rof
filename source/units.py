from enum import Enum
from source.cards import Card
from source import constants

""" Represents individual units on the tabletop """

class UnitType(Enum):
    Infantry = 0
    Cavalry = 1
    Artillery = 2
    Other = 3

""" Base class for all Units """
class Unit:
    commander : str
    unitType: UnitType
    nickname: str
    steadiness: Card
    armour: int

    def __init__(self, commander, unitType, nickname=""):
        self.commander = commander
        self.unitType = unitType
        self.nickname = nickname
        self.armour = 0
        self.steadiness = constants.DEFAULT_STEADINESS

    def name(self) -> str:
        if self.nickname:
            return self.nickname

        if self.unitType == UnitType.Infantry:
            return f"{self.commander}'s Regiment of Foote"
        elif self.unitType == UnitType.Cavalry:
            return f"{self.commander}'s Regiment of Horse"
        elif self.unitType == UnitType.Artillery:
            return f"{self.commander}'s battery of guns"
        return f"{self.commander}'s men"
    
    def strength(self) -> int:
        return 0

    def setSteadiness(self, steadiness: Card) -> None:
        self.steadiness = steadiness

    def setArmour(self, armour: int) -> None:
        self.armour = armour

    def ferocity(self) -> int:
        return 0

    def firepower(self) -> int:
        return 0

class InfantryUnit(Unit):
    pike: int # How many pikemen are in the unit
    shot: int # How many musketeers are in the unit

    def __init__(self, commander, pike, shot, nickname=""):
        super().__init__(commander, UnitType.Infantry, nickname)
        self.pike = pike
        self.shot = shot

    def ferocity(self) -> int:
        return self.pike // 4

    def firepower(self) -> int:
        return self.shot // 8

    def strength(self) -> int:
        return self.pike + self.shot