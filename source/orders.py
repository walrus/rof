from source.units import Unit, CavalryUnit, CavalryMovementSpeed, InfantryUnit

#TODO: how best to represent E.G move direction or shooting target?

class Order:
    """ Represents an order a Player might give to a Unit"""
    name: str
    description: str
    baseDifficulty: int    # All orders have a base difficulty; 
    addsDisorder: bool     # Some are modified by the Unit's Disorder
    #prerequisite: function # Some have special prerequisites; specified by a function which takes a Unit

    def __init__(self, name, description, baseDifficulty, addsDisorder = False, prerequisite = None):
        self.name = name
        self.description = description
        self.baseDifficulty = baseDifficulty
        self.addsDisorder = addsDisorder
        self.prerequisite = prerequisite

    def currentDifficulty(self, unit: Unit) -> int:
        return self.baseDifficulty + unit.disorder if self.addsDisorder else self.baseDifficulty

    def isPossible(self, highestCardCombo: int, unit: Unit) -> bool:
        difficulty = self.currentDifficulty(unit)
        meetsPrerequisite = not self.prerequisite or self.prerequisite(unit) 
        return highestCardCombo >= difficulty and meetsPrerequisite

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
