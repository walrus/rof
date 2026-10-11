from collections.abc import Callable
from enum import Enum
from math import ceil, sqrt

from source.cards import Card, Rank, Suit, allAces, allKings, draw, sumCards
from source.constants import MUSKET_RANGE, PISTOL_RANGE, Faction

""" Represents individual units on the tabletop """

class UnitType(Enum):
    Infantry = 0
    Cavalry = 1
    Artillery = 2
    Other = 3

class MoraleState(Enum):
    OK = 0
    Wavering = 1
    Panicked = 2

class MovementSpeed(Enum):
    Halt   = 0
    Slow   = 1
    Walk   = 2
    Run    = 3 # Only for infantry
    Trot   = 4 # Only for cavalry
    Gallop = 5 # Only for cavalry

def moveSpeedFromOrder(string : str, unitType: UnitType) -> MovementSpeed:
    """ Convert a given Order into a movement speed """
    if string == "Reform":
        return MovementSpeed.Slow
    elif string == "Flee":
        return MovementSpeed.Gallop if unitType == UnitType.Cavalry else MovementSpeed.Run

    return MovementSpeed[string]

""" Base class for all Units """
class Unit:
    commander : str
    unitType: UnitType
    nickname: str
    steadiness: Card
    armour: int
    faction: Faction
    morale: MoraleState
    disorder: int
    shooting: bool # Is this unit currently shooting
    fighting: bool # Is this unit currently fighting
    position: tuple[int, int] # xy; height is ignored for now
    # Note also that all units must implement movementSpeed
    currentOrder: Order | None  # noqa: F821
    currentMovementSpeed: MovementSpeed

    def __init__(self, commander, unitType, faction, nickname=""):
        self.commander = commander
        self.unitType = unitType
        self.nickname = nickname
        self.armour = 0
        self.faction = faction # TODO: pass in faction from owning Player
        self.morale = MoraleState.OK
        self.disorder = 0
        self.shooting = False
        self.fighting = False
        self.position = (0, 0)
        self.currentOrder = None
        self.steadiness = Card.fromRankAndSuit(Rank.Nine, Suit.Clubs)
        self.currentMovementSpeed = MovementSpeed.Halt

    # Setters, mostly fixed for Unit lifetime
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
    
    def setSteadiness(self, steadiness: Card) -> None:
        self.steadiness = steadiness

    def setArmour(self, armour: int) -> None:
        self.armour = armour

    # Status, implemented by subclasses 
    def strength(self) -> int:
        return 0

    def ferocity(self) -> int:
        return 0

    def firepower(self) -> int:
        return 0

    def isOK(self) -> bool:
        return self.morale == MoraleState.OK

    def wavering(self) -> bool:
        return self.morale == MoraleState.Wavering

    def panicked(self) -> bool:
        return self.morale == MoraleState.Panicked

    def fitToFight(self):
        return self.strength() > 0 and not self.panicked()

    def takeCasualties(self, num: int) -> None:
        pass

    # Deal with Orders

    def carryOut(self, order: Order) -> None:  # noqa: F821 (I'll deal with it!)
        """ Attempt to carry out the given order"""
        if not order:
            # Carry on as you were 
            # TODO: Things like Halt should clear for neatness, but will have essentially the same effect 
            # if they get enacted every turn so low priority
            if self.currentOrder:
                self.carryOut(self.currentOrder)
            return

        self.currentOrder = order

        match order.name:
            case 'Halt':
                self.halt()
            case 'Walk' | 'Run' | 'Reform' | 'Trot' | 'Gallop' | 'Flee':
                moveSpeed = moveSpeedFromOrder(order.name, self.unitType)
                self.move(order.direction, moveSpeed) # pyright: ignore[reportArgumentType]
            case 'Fire':
                self.shootAt(order.target) # pyright: ignore[reportArgumentType] (guaranteed to not be None for this Order type)
            case 'Cease Fire':
                self.ceaseFire()
            case 'Rally':
                self.rally()
            case 'Encourage':
                self.encourage()
            case 'Charge':
                self.charge(order.target) # pyright: ignore[reportArgumentType]
            case _:
                print(f"Unknown Order given: {order.name}")
        return

    def halt(self) -> None:
        self.currentMovementSpeed = MovementSpeed.Halt

    def move(self, direction: tuple[int, int], speed) -> None:
        pass

    def shootAt(self, target: "Unit") -> None:
        pass

    def ceaseFire(self) -> None:
        self.shooting = False

    def rally(self) -> None:
        pass

    def encourage(self) -> None:
        pass

    def charge(self, target: "Unit") -> None:
        pass

    def panicTest(self) -> bool:
        # If you're already panicked then you fail additional panic tests
        if self.morale == MoraleState.Panicked:
            return False
        
        if self.commander:
            panicCards = draw(2, 2)
        else:
            panicCards = draw(3, 2, False)

        # Panic test always passed on two Kings, and always failed on two Aces
        if allKings(panicCards) or not (allAces(panicCards) and sumCards(panicCards) >= self.disorder):
            return True

        if self.morale == MoraleState.Wavering:
            self.morale = MoraleState.Panicked
        else:
            self.morale = MoraleState.Wavering

        return False

    def directionOf(self, target: "Unit") -> tuple[int, int]:
        """ Vector in the direction of target """
        xDist = target.position[0] - self.position[0]
        yDist = target.position[1] - self.position[1]
        return (xDist, yDist)

    def distanceTo(self, target: "Unit") -> int: # Not Self because subclasses can call this too
        """ Cartesian distance to target, rounded up to the nearest inch"""
        xDist, yDist = self.directionOf(target)
        return ceil(sqrt((xDist * xDist) + (yDist * yDist)))

    def inRange(self, target: "Unit") -> bool: # Not Self - any subclass can check range to any other subclass
        return False

    def isEnemy(self, faction: Faction) -> bool:
        return faction != self.faction

class InfantryUnit(Unit):
    pike: int # How many pikemen are in the unit
    shot: int # How many musketeers are in the unit

    def __init__(self, commander, faction, pike, shot, nickname=""):
        super().__init__(commander, UnitType.Infantry, faction, nickname)
        self.pike = pike
        self.shot = shot
        self.unitType = UnitType.Infantry

    def ferocity(self) -> int:
        return self.pike // 4

    def firepower(self) -> int:
        return self.shot // 8

    def strength(self) -> int:
        return self.pike + self.shot

    def inRange(self, target: Unit) -> bool:
        return self.distanceTo(target) <= MUSKET_RANGE

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

class CavalryUnit(Unit):
    horse: int # Number of horsemen in the unit

    def __init__(self, commander, faction, horse, nickname=""):
        super().__init__(commander, UnitType.Cavalry, faction, nickname)
        self.horse = horse
        self.unitType = UnitType.Cavalry

    def ferocity(self) -> int:
        return self.horse // 2

    def firepower(self) -> int:
        return self.horse // 4

    def strength(self) -> int:
        return self.horse

    def inRange(self, target: Unit) -> bool:
        return self.distanceTo(target) <= PISTOL_RANGE


class Order:
    """ Represents an order a Player might give to a Unit 
        Tightly coupled because most Orders have a prerequisite which depends on a Unit"""
    name: str
    description: str
    baseDifficulty: int    # All orders have a base difficulty; 
    addsDisorder: bool     # Some are modified by the Unit's Disorder
    prerequisite: Callable | None # Some have special prerequisites; specified by a function which takes a Unit
    target: Unit | None
    direction: tuple[int, int] | None

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
    Order("Halt", "Stop what you're doing", 5, True, lambda u: u.currentMovementSpeed.value > 0 and u.currentMovementSpeed != MovementSpeed.Gallop),
    Order("Walk", "Move slowly forwards", 5, True, None),
    Order("Run", "Move quickly forwards", 5, True, lambda u: isinstance(u, InfantryUnit)),
    Order("Reform", "Move slowly into a new formation", 5, True, None),
    Order("Flee", "Run away!", 5, False, None),
    Order("Rally", "Stop running away!", 0, False, lambda u: not u.isOK()),
    Order("Encourage", "Make the troops feel better", 0, False, lambda u: u.disorder > 0),
    Order("Charge", "Move quickly towards the enemy", 5, True, lambda u: u.isOK()),
    Order("Trot", "Cavalry move fairly quickly forwards", 5, True, lambda u: isinstance(u, CavalryUnit)),
    Order("Gallop", "Cavalry move quickly forwards", 5, True, lambda u: isinstance(u, CavalryUnit) and u.currentMovementSpeed == MovementSpeed.Trot),
    Order("Fire", "Start shooting", 5, False, lambda u: u.firepower() > 0 and not u.shooting),
    Order("Cease Fire", "Stop shooting", 5, True, lambda u: u.shooting),
]