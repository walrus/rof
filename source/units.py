from enum import Enum
from math import ceil, sqrt
from source.cards import Card, draw, sumCards, allAces, allKings
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
    event: bool # TODO: Events table once the core game is running OK

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
    shooting: bool # Is this unit currently shooting
    fighting: bool # Is this unit currently fighting
    position: tuple[int, int] # xy; height is ignored for now
    # Note also that all units must implement movementSpeed
    # currentOrder: Order 

    def __init__(self, commander, unitType, nickname=""):
        self.commander = commander
        self.unitType = unitType
        self.nickname = nickname
        self.armour = 0
        self.panic = PanicState.OK
        self.disorder = 0
        self.shooting = False
        self.fighting = False
        self.position = (0, 0)
        self.currentOrder = None
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

    def carryOut(self, order: Order):# -> Outcome:
        """ Attempt to carry out the given order"""
        if not order:
            # Carry on as you were
            if self.currentOrder:
                return self.carryOut(self.currentOrder)
            else:
                return Outcome(0, 0, False, None)
        #TODO actually do the thing. Guess I need to encode something within the Order that says what actually happens?
        # Or maybe the Unit needs to encode it?
        return Outcome(0, 0, False, None)

    def panicTest(self) -> bool:
        # If you're already panicked then you fail additional panic tests
        if self.panic == PanicState.Panicked:
            return False
        
        if self.commander:
            panicCards = draw(2, 2)
        else:
            panicCards = draw(3, 2, False)

        # Panic test always passed on two Kings, and always failed on two Aces
        if allKings(panicCards):
            return True
        elif not allAces(panicCards) and sumCards(panicCards) >= self.steadiness:
            return True

        if self.panic == PanicState.Wavering:
            self.panic = PanicState.Panicked
        else:
            self.panic = PanicState.Wavering

        return False

    def applyOutcome(self, outcome: Outcome) -> bool:
        self.disorder = self.disorder + outcome.disorder
        self.takeCasualties(outcome.casualties)

        if (outcome.panic):
            return self.panicTest()
        return True

    def isOK(self) -> bool:
        return self.panic == PanicState.OK

    def wavering(self) -> bool:
        return self.panic == PanicState.Wavering

    def panicked(self) -> bool:
        return self.panic == PanicState.Panicked

    def fitToFight(self):
        return self.strength() > 0 and not self.panicked()

    def distanceTo(self, target: Unit) -> int:
        """ Cartesian distance to target, rounded up to the nearest inch"""
        xDist = target.position[0] - self.position[0]
        yDist = target.position[1] - self.position[1]
        return ceil(sqrt((xDist * xDist) + (yDist * yDist)))

    def inRange(self, target: Unit) -> bool:
        return False

class InfantryMovementSpeed(Enum):
    Halt = 0
    Walk = 1
    Run = 2

class InfantryUnit(Unit):
    pike: int # How many pikemen are in the unit
    shot: int # How many musketeers are in the unit
    movementSpeed: InfantryMovementSpeed

    def __init__(self, commander, pike, shot, nickname=""):
        super().__init__(commander, UnitType.Infantry, nickname)
        self.pike = pike
        self.shot = shot
        self.unitType = UnitType.Infantry
        self.movementSpeed = InfantryMovementSpeed.Halt

    def ferocity(self) -> int:
        return self.pike // 4

    def firepower(self) -> int:
        return self.shot // 8

    def strength(self) -> int:
        return self.pike + self.shot

    def inRange(self, target: Unit) -> bool:
        return self.distanceTo(target) <= constants.MUSKET_RANGE

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

class CavalryMovementSpeed(Enum):
    Halt = 0
    Walk = 1
    Trot = 2
    Gallop = 3

class CavalryUnit(Unit):
    movementSpeed: CavalryMovementSpeed
    horse: int # Number of horsemen in the unit

    def __init__(self, commander, horse, nickname=""):
        super().__init__(commander, UnitType.Cavalry, nickname)
        self.horse = horse
        self.unitType = UnitType.Infantry
        self.movementSpeed = CavalryMovementSpeed.Halt

    def ferocity(self) -> int:
        return self.horse // 2

    def firepower(self) -> int:
        return self.horse // 4

    def strength(self) -> int:
        return self.horse

    def inRange(self, target: Unit) -> bool:
        return self.distanceTo(target) <= constants.PISTOL_RANGE


class Order:
    """ Represents an order a Player might give to a Unit 
        Tightly coupled because most Orders have a prerequisite which depends on a Unit"""
    name: str
    description: str
    baseDifficulty: int    # All orders have a base difficulty; 
    addsDisorder: bool     # Some are modified by the Unit's Disorder
    #prerequisite: function # Some have special prerequisites; specified by a function which takes a Unit
    # target: Unit TODO: figure out how type hints work for nullable fields
    #direction: tuple[int, int]

    def __init__(self, name, description, baseDifficulty, addsDisorder = False, prerequisite = None):
        self.name = name
        self.description = description
        self.baseDifficulty = baseDifficulty
        self.addsDisorder = addsDisorder
        self.prerequisite = prerequisite
        self.target = None
        self.direction = None

    def currentDifficulty(self, unit: Unit) -> int:
        return self.baseDifficulty + unit.disorder if self.addsDisorder else self.baseDifficulty

    def isPossible(self, highestCardCombo: int, unit: Unit) -> bool:
        difficulty = self.currentDifficulty(unit)
        meetsPrerequisite = not self.prerequisite or self.prerequisite(unit) 
        return highestCardCombo >= difficulty and meetsPrerequisite

    def setTarget(self, target: Unit) -> None:
        self.target = target

    def setDirection(self, direction: tuple[int,int]) -> None:
        self.direction = direction

# Common orders that most units can carry out
# description, base difficulty, adds disorder, prerequisite
basicOrders = [
    Order("Halt", "Stop what you're doing", 5, True, lambda u: u.shooting or u.movementSpeed.value > 0),
    Order("Walk", "Move slowly forwards", 5, True, None),
    Order("Run", "Move quickly forwards", 5, True, lambda u: isinstance(u, InfantryUnit)),
    Order("Reform", "Move slowly into a new formation", 5, True, None),
    Order("Flee", "Run away!", 5, False, None),
    Order("Rally", "Stop running away!", 0, False, lambda u: not u.isOK()),
    Order("Encourage", "Make the troops feel better", 0, False, lambda u: u.disorder > 0),
    Order("Charge", "Move quickly towards the enemy", 5, True, lambda u: u.isOK()),
    Order("Trot", "Cavalry move fairly quickly forwards", 5, True, lambda u: isinstance(u, CavalryUnit)),
    Order("Gallop", "Cavalry move quickly forwards", 5, True, lambda u: isinstance(u, CavalryUnit) and u.movementSpeed == CavalryMovementSpeed.Trot),
    Order("Fire", "Start shooting", 5, False, lambda u: u.firepower() > 0 and not u.shooting),
    Order("Cease Fire", "Stop shooting", 5, True, lambda u: u.shooting),
]