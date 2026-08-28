from enum import Enum
from math import ceil
from source.cards import Card, draw, drawSingle
from source import constants

""" Represents individual units on the tabletop """

class UnitType(Enum):
    Infantry = 0
    Cavalry = 1
    Artillery = 2
    Other = 3

class PanicState(Enum):
    OK = 0
    Wavering = 1
    Panicked = 2


""" Describes the change in state of a Unit after an Action """
class Outcome:
    casualties: int
    disorder: int
    panic: bool
    event: bool # TODO: work out how to encode the events table

    def __init__(self, casualties, disorder, panic, event) -> None:
        self.casualties = casualties
        self.disorder = disorder
        self.panic = panic
        self.event = event

    def anyChange(self) -> bool:
        return self.casualties > 0 or self.disorder != 0 or self.panic or self.event

""" Base class for all Units """
class Unit:
    commander : str
    unitType: UnitType
    nickname: str
    steadiness: Card
    armour: int
    panic: PanicState
    disorder: int

    def __init__(self, commander, unitType, nickname=""):
        self.commander = commander
        self.unitType = unitType
        self.nickname = nickname
        self.armour = 0
        self.panic = PanicState.OK
        self.disorder = 0
        #self.steadiness = constants.DEFAULT_STEADINESS

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

    def takeCasualties(self, num: int) -> None:
        pass

    def panicTest(self) -> bool:
        # If you're already panicked then you fail additional panic tests
        if self.panic == PanicState.Panicked:
            return False
        
        # TODO: unattached officer
        panicCard = drawSingle()

        # Panic test passed!
        if panicCard >= self.steadiness:
            return True

        if self.panic == PanicState.Wavering:
            print(f"{self.name()} is PANICKED")
            self.panic = PanicState.Panicked
        else:
            print(f"{self.name()} is WAVERING!")
            self.panic = PanicState.Wavering

        return False

    def applyOutcome(self, outcome: Outcome) -> bool:
        self.disorder = self.disorder + outcome.disorder
        self.takeCasualties(outcome.casualties)

        if (outcome.panic):
            print("### panic test!")
            return self.panicTest()
        return True

    def wavering(self) -> bool:
        return self.panic == PanicState.Wavering

    def panicked(self) -> bool:
        return self.panic == PanicState.Panicked

    def fitToFight(self):
        return self.strength() > 0 and not self.panicked()
    
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

    def takeCasualties(self, num: int) -> None:
        if num == 0:
            return

        #TODO combat casualties handled differently
        #TODO handle running out of pike or shot

        # shot take first cas, then equally split
        shotCasualties = ceil(num * (2 / 3))
        pikeCasualties = num - shotCasualties

        if not self.pike:
            shotCasualties = shotCasualties + pikeCasualties
        if not self.shot:
            pikeCasualties = pikeCasualties + shotCasualties
        
        print(f"Lost {pikeCasualties} pike and {shotCasualties} shot")

        if self.pike > pikeCasualties:
            self.pike = self.pike - pikeCasualties
        else:
            self.pike = 0

        if self.shot > shotCasualties:
            self.shot = self.shot - shotCasualties
        else:
            self.shot = 0