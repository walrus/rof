from collections.abc import Callable
from enum import Enum
from math import atan, ceil, cos, sin, sqrt

from source.cards import (
    Card,
    Rank,
    Suit,
    allAces,
    allKings,
    draw,
    numAboveThreshold,
    numAces,
    sumCards,
)
from source.constants import (
    AUTO_PANIC_THRESHOLD,
    BEST_OF_FIGHTING,
    BEST_OF_SHOOTING,
    MIN_FIGHTING_THRESHOLD,
    MIN_SHOOTING_DISTANCE,
    MUSKET_RANGE,
    PANIC_THRESHOLD,
    PISTOL_RANGE,
    SINGLE_CARD_CHARGE_MAX,
    TWO_CARD_CHARGE_MAX,
    Faction,
)

""" Represents individual units on the tabletop """

class UnitType(Enum):
    Infantry = 0
    Cavalry = 1
    Artillery = 2
    Other = 3

class MoraleState(Enum):
    OK        = 0 # Doing fine
    Wavering  = 1 # Doing badly but still under control
    Panicked  = 2 # Running away, but could be rallied
    Dispersed = 3 # Completely broken; unrally-able

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

def cardDrawFromMovementSpeed(speed : MovementSpeed) -> list[Card]:
    match speed:
        case MovementSpeed.Halt:
            return []
        case MovementSpeed.Slow:
            return draw(2, 1, False) # 2 cards, keep lowest
        case MovementSpeed.Walk:
            return draw(1, 1)
        case MovementSpeed.Run | MovementSpeed.Trot:
            return draw(2, 1) # 2 cards, keep highest
        case MovementSpeed.Gallop:
            return draw(2, 2)
        case _:
            return []

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
    shootingDistanceMultiplier: int # TODO: make a proper constant

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

    # Status, mostly implemented by subclasses 
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

    def dispersed(self) -> bool:
        return self.morale == MoraleState.Dispersed
    
    def fitToFight(self) -> bool:
        return self.strength() > 0 and not (self.panicked() or self.dispersed())

    def takeCasualties(self, num: int) -> None:
        pass

    def disperse(self) -> None:
        self.morale = MoraleState.Dispersed

    # Deal with Orders

    def carryOut(self, order: Order) -> None:  # noqa: F821 (I'll deal with it!)
        """ Attempt to carry out the given order"""
        #TODO check for Fighting and Fleeing as those interact with Orders a little differently
        if not order:
            # Carry on as you were 
            # TODO: Things like Halt should clear for neatness, but will have essentially the same effect 
            # if they get enacted every turn so low priority
            if self.currentOrder:
                print(f"{self.name()} continues to {self.currentOrder.name}")
                self.carryOut(self.currentOrder)
            return

        # E.G don't stop firing just because of encouragement
        if order.name not in ['Encourage']:
            self.currentOrder = order

        match order.name:
            case 'Halt':
                self.halt()
            case 'Walk' | 'Run' | 'Reform' | 'Trot' | 'Gallop':
                moveSpeed = moveSpeedFromOrder(order.name, self.unitType)
                self.move(order.direction, moveSpeed) # pyright: ignore[reportArgumentType]
            case 'Flee':
                self.flee(order.direction) # pyright: ignore[reportArgumentType]
            case 'Fire':
                self.shootAt(order.target) # pyright: ignore[reportArgumentType] (guaranteed to not be None for this Order type)
            case 'Cease Fire':
                self.ceaseFire()
            case 'Rally':
                self.rally()
            case 'Encourage':
                self.encourage(order.cardsUsed)
            case 'Charge':
                self.charge(order.target) # pyright: ignore[reportArgumentType]
            case _:
                print(f"Unknown Order given: {order.name}")
        return

    def halt(self) -> None:
        self.currentMovementSpeed = MovementSpeed.Halt

    def move(self, direction: tuple[int, int], speed: MovementSpeed, stopAtDestination=False) -> None:
        cardsDrawn = cardDrawFromMovementSpeed(speed)
        distance = sumCards(cardsDrawn)

        if speed == MovementSpeed.Run:
            self.disorder = self.disorder + 1
        elif speed == MovementSpeed.Gallop:
            self.disorder = self.disorder + 1
            if numAboveThreshold(cardsDrawn, self.dash): # pyright: ignore[reportAttributeAccessIssue] cavalry units definitely have this
                self.blown = True
        
        moveVector = ()
        # Handle moves along an axis:
        if direction[0] == 0:
            moveVector = (0, distance if direction[1] > 0 else -distance)
        elif direction[1] == 0:
            moveVector = (distance if direction[0] > 0 else -distance, 0)
        else:
            # Transform cartesian distance moved into x,y, rounding to the nearest int
            angle = atan(direction[0] / direction[1])
            distX = cos(angle) * distance
            distY = sin(angle) * distance
            moveVector = (distX, distY)

        if stopAtDestination:
            moveVector = (max(moveVector[0], direction[0]), max(moveVector[1], direction[1]))

        print(f"Moving: {moveVector[0]},{moveVector[1]}")
        self.position = (self.position[0] + round(moveVector[0]), self.position[1] + round(moveVector[1]))
        #print(f"New position {self.position[0]},{self.position[1]}")

    def charge(self, target: "Unit") -> None:
        # Before you charge, have to check to see if your men baulk, or theirs flee
        if not self.panicTest():
            print(f"{self.name()} baulks and fails to charge {target.name()}")
            self.morale = MoraleState.Wavering
            return

        target.panicTest()
        if target.panicked():
            # If the target Panics (not just Wavers) then a combat _probably_ won't happen
            print(f"{target.name()} runs rather than stand and fight {self.name()}")
            target.flee(self.directionOf(target))
    
        speed = MovementSpeed.Gallop if self.unitType == UnitType.Cavalry else MovementSpeed.Run
        self.move(self.directionOf(target), speed, True)

        if self.distanceTo(target) < 1:
            # caught them! If they're fleeing, then they're dispersed
            if target.panicked():
                print(f"{self.name()} disperses {target.name()}")
                target.disperse()
            else:
                print(f"{self.name()} charges {target.name()}")
                self.fight(target)
    
    def fight(self, target: "Unit") -> None:
        # Calculate our effects on the enemy first but apply them simultaneously!
        enemyCasualtyThreshold = MIN_FIGHTING_THRESHOLD + target.armour
        friendlyCards = draw(self.ferocity(), BEST_OF_FIGHTING)
    
        enemyCasualties = sumCards(friendlyCards) // enemyCasualtyThreshold
        enemyDisorder = enemyCasualties + numAboveThreshold(friendlyCards, target.steadiness)

        # Now calculate the enemy's
        friendlyCasualtyThreshold = MIN_FIGHTING_THRESHOLD + self.armour
        enemyCards = draw(target.ferocity(), BEST_OF_FIGHTING)
    
        friendlyCasualties = sumCards(enemyCards) // friendlyCasualtyThreshold
        friendlyDisorder = friendlyCasualties + numAboveThreshold(enemyCards, self.steadiness)

        ## Add any self-disorder from Aces and ensure you always take at least one
        enemyDisorder = max(1, enemyDisorder + numAces(enemyCards))
        friendlyDisorder = max(1, friendlyDisorder + numAces(friendlyCards))

        # Now apply the effects
        target.takeCasualties(enemyCasualties)
        target.disorder = target.disorder + enemyDisorder
        print(f"{target.name()} takes {enemyCasualties} casualties and {enemyDisorder} disorder")

        self.takeCasualties(friendlyCasualties)
        self.disorder = self.disorder + friendlyDisorder
        print(f"{self.name()} takes {friendlyCasualties} casualties and {friendlyDisorder} disorder")

        # Finally, trigger panic tests first for the loser and then (if they don't run) the winner
        loser = target
        winner = self
        if friendlyCasualties > enemyCasualties or (friendlyCasualties == enemyCasualties and friendlyDisorder > enemyDisorder):
            loser = self
            winner = target

        print(f"{winner.name()} wins this round!")

        # Take panic tests - a failed test here results in a Panic not just Wavering
        # If both sides are still around, then they're both fighting (TODO: except Cavalry!)
        #TODO implement pursuit as an Order type?
        if not loser.panicTest():
            # Loser runs away
            loser.flee(winner.directionOf(loser))
            winner.fighting = False
            print(f"{loser.name()} runs away after losing!")
        elif not winner.panicTest():
            # Winner ran away! # TODO: this won't work if fighting units end up right on top of each other
            winner.flee(loser.directionOf(winner))
            loser.fighting = False
            print(f"{winner.name()} runs away despite winning!")
        else:
            self.fighting = True
            target.fighting = True
            print("Both sides stay in the fight for another round")


    def flee(self, direction: tuple[int, int]) -> None:
        speed = MovementSpeed.Run
        if self.unitType == UnitType.Cavalry:
            speed = MovementSpeed.Gallop if not self.blown else MovementSpeed.Trot

        self.move(direction, speed)

    def shootAt(self, target: "Unit") -> None:
        distance = max(MIN_SHOOTING_DISTANCE, (self.distanceTo(target) * self.shootingDistanceMultiplier))
        cards = draw(self.firepower(), BEST_OF_SHOOTING)
    
        casualties = sumCards(cards) // distance
        enemyDisorder = casualties + numAboveThreshold(cards, target.steadiness)

        print(f"{target.name()} takes {casualties} casualties and {enemyDisorder} disorder")
        target.takeCasualties(casualties)
        target.disorder = target.disorder + enemyDisorder
        enemyPanic = enemyDisorder >= PANIC_THRESHOLD or target.disorder >= AUTO_PANIC_THRESHOLD
        if enemyPanic:
            target.panicTest() # We don't need to know if they panicked
        
        self.disorder = self.disorder + numAces(cards)

        #TODO shooting events
        #enemyEvent = allFaceCards(cards)
        #friendlyEvent = allAces(cards)

    def ceaseFire(self) -> None:
        self.shooting = False

    def rally(self) -> None:
        """ Attempt to rally a Panicked unit back to Wavering, or a Wavering unit back to OK"""
        if self.dispersed or not self.moraleCheck():
            return

        if self.morale == MoraleState.Wavering:
            print(f"{self.name()} is rallied to OK again")
            self.morale = MoraleState.OK
        else:
            print(f"{self.name()} is rallied back to Wavering")
            self.morale = MoraleState.Wavering

    def encourage(self, cardsUsed: list[Card]) -> None:
        totalDisorderRemoved = sum(2 if card.rank() >= Rank.Jack else 1 for card in cardsUsed)
        print(f"{self.name()} removed {totalDisorderRemoved} disorder by encouragement")
        self.disorder = max(0, self.disorder - totalDisorderRemoved)

    def moraleCheck(self) -> bool:
        # True if passed, false otherwise
        if self.commander:
            panicCards = draw(2, 2)
        else:
            panicCards = draw(3, 2, False)

        # Morale tests always passed on two Kings, and always failed on two Aces
        return allKings(panicCards) or (not allAces(panicCards) and sumCards(panicCards) >= self.disorder)

    def panicTest(self, immediatelyPanic: bool = False) -> bool:
        # If you're already panicked then you fail additional panic tests (but you only disperse if charged)
        if self.morale == MoraleState.Panicked:
            return False

        if self.moraleCheck():
            return True

        if immediatelyPanic or self.morale == MoraleState.Wavering:
            print(f"{self.name()} is panicked!")
            self.morale = MoraleState.Panicked
        else:
            print(f"{self.name()} is wavering!")
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

    def inChargeRange(self, target: "Unit") -> bool:
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
        self.shootingDistanceMultiplier = 1

    def ferocity(self) -> int:
        return self.pike // 4

    def firepower(self) -> int:
        return self.shot // 8

    def strength(self) -> int:
        return self.pike + self.shot

    def inRange(self, target: Unit) -> bool:
        return self.distanceTo(target) <= MUSKET_RANGE

    def inChargeRange(self, target: Unit) -> bool:
        return self.distanceTo(target) <= SINGLE_CARD_CHARGE_MAX

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
    dash: Card
    blown: bool

    def __init__(self, commander, faction, horse, nickname=""):
        super().__init__(commander, UnitType.Cavalry, faction, nickname)
        self.horse = horse
        self.unitType = UnitType.Cavalry
        self.shootingDistanceMultiplier = 2
        self.dash = Card.fromRankAndSuit(Rank.Eight, Suit.Clubs)
        self.blown = False

    def ferocity(self) -> int:
        return self.horse // 2

    def firepower(self) -> int:
        return self.horse // 4

    def strength(self) -> int:
        return self.horse

    def inRange(self, target: Unit) -> bool:
        return self.distanceTo(target) <= PISTOL_RANGE

    def inChargeRange(self, target: Unit) -> bool:
        distance = self.distanceTo(target)
        return distance <= SINGLE_CARD_CHARGE_MAX if self.blown else distance <= TWO_CARD_CHARGE_MAX

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
    cardsUsed: list[Card]

    def __init__(self, name, description, baseDifficulty, addsDisorder = False, prerequisite = None):
        self.name = name
        self.description = description
        self.baseDifficulty = baseDifficulty
        self.addsDisorder = addsDisorder
        self.prerequisite = prerequisite
        self.target = None
        self.direction = None
        self.cardsUsed = []

    def currentDifficulty(self, unit: Unit) -> int:
        return self.baseDifficulty + unit.disorder if self.addsDisorder else self.baseDifficulty

    def isPossible(self, highestCardCombo: int, unit: Unit, enemies: list[Unit]) -> bool:
        # Global prerequisites: can't issue orders to a Dispersed unit
        if unit.dispersed():
            return False

        # can't issue orders while fighting or panicked, except to Rally, Encourage or Flee
        if (unit.fighting or unit.panicked()) and self.name not in ['Rally', 'Encourage', 'Flee']:
            return False

        # Can't Fire or Charge if not in range
        if self.name == 'Fire' and not any(unit.inRange(enemy) for enemy in enemies):
            return False
        if self.name == 'Charge' and not any(unit.inChargeRange(enemy) for enemy in enemies):
            return False

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
    Order("Run", "Move quickly forwards", 5, True, lambda u: u.unitType == UnitType.Infantry),
    Order("Reform", "Move slowly into a new formation", 5, True, None),
    Order("Flee", "Run away!", 5, False, None),
    Order("Rally", "Stop running away!", 1, False, lambda u: not u.isOK()),
    Order("Encourage", "Make the troops feel better", 1, False, lambda u: u.disorder > 0),
    Order("Charge", "Move quickly towards the enemy", 5, True, lambda u: u.isOK()),
    Order("Trot", "Cavalry move fairly quickly forwards", 5, True, lambda u:u.unitType == UnitType.Cavalry),
    Order("Gallop", "Cavalry move quickly forwards", 5, True, lambda u: u.unitType == UnitType.Cavalry and u.currentMovementSpeed == MovementSpeed.Trot and not u.blown),
    Order("Fire", "Start shooting", 5, False, lambda u: u.firepower() > 0 and not u.shooting),
    Order("Cease Fire", "Stop shooting", 5, True, lambda u: u.shooting),
]