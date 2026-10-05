""" Commission of Array: a pre-game Colonel generator for Regiment of Foote """

from source.cards import Card, draw, Rank, drawSingle
from random import randint, sample, shuffle

from enum import Enum, IntEnum

forenames = {
    "salts": # Salts of the Earth 
    ["Philip", "Thomas", "William", "Richard", "John", "Nathaniel", "Edward", "James", "George", "Edmund"],
    "cavaliers": # Charismatic Cavaliers
    ["Bevil", "Fulk", "Gervase", "Kenelm", "Marmaduke", "Ralph", "Gilbert", "Maurice", "Rupert", "Charles"],
    "parliamentarians": # Plain-speaking Parliament Men
    ["Denzel", "Zouch", "Hardress", "Humphrey", "Bulstrode", "Erasmus", "Herbert", "Brampton", "Arthur", "Oliver"],
    "puritans": # Pious Puritans
    ["Elijah", "Abraham", "Jeremiah", "Theophilious", "Makepeace", "Perseverance", "Stedfast", "Praise-God", "Faithfull", "Posthumous"],
}

surnames = {
    "salts": # Salts of the Earth
    ["Legge", "Browne", "Blagge", "Willys", "Whalley", "Sprigge", "Crispe", "Lumby", "Wallop", "Cheek"],
    "cavaliers": # Charismatic Cavaliers
    ["Grenville", "Hunke", "Wemyss", "Digby", "Langdale", "Hopton", "Widdrington", "Wormesley", "Dyve", "Ogle"],
    "parliamentarians": # Plain-speaking Parliament Men
    ["Holles", "Tate", "Waller", "Glemham", "Okey", "Pye", "Pim", "Gurdon", "Hesilrige", "Cromwell"],
    "puritans": # Pious Puritans
    ["Blindlosse", "Meldrum", "Sexby", "Windebank", "Twistleton", "Pride", "Wroth", "Yonge", "Fortescue", "Wagstaffe"]
}

estates = [
    "Stratfield Saye",
    "Turgis Green",
    "Silchester",
    "Mapledurwell",
    "Upton Grey",
    "Nately Scures",
    "Hook",
    "Bramley",
    "Sherborne",
    "Heckfield",
]

class Faction(Enum):
    Royalist = 0
    Parliamentarian = 1
    # Maybe I'll add the Scots later...

class Title(IntEnum):
    Commoner = 0
    Knight = 1
    Baronet = 2
    Baron = 3
    Viscount = 4
    Earl = 5
    Marquess = 6
    Duke = 7

# Personal characteristics relevant to command
class Trait(Enum):
    Hotheaded = 0 # Must get stuck in to combat
    Cowardly = 1  # Cannot get stuck in to combat
    Sharp = 2     # +1 grip
    Poltroon = 3  # -1 grip
    Handsome = 4  # +1 status
    Unsightly = 5 # -1 status
    Wealthy = 6   # Extra wealth
    Dissolute = 7 # Less wealth
    Stern = 8     # +1 steadiness
    Fussy = 9     # -1 steadiness

# Past experiences and positions relevant to command
class Position(Enum):
    Merchant = 0
    JP = 1
    MP = 2
    Judge = 3
    Clergy = 4
    Governer = 5
    Commander = 6 # AKA past military experience

positionPrerequisites = {
    Position.Merchant: lambda x : x.title <= Title.Baronet,
    Position.JP: lambda x : x.title <= Title.Baron,
    Position.MP: lambda x : x.title <= Title.Baron,
    Position.Judge: lambda x : x.title <= Title.Baron,
    Position.Clergy: lambda x : x.title <= Title.Baron and x.piety > 3,
    Position.Governer: lambda x : x.status > 5,
    Position.Commander: lambda x : x.grip > 2 or x.status > 7
}

class Colonel:
    faction: Faction
    piety: int
    title: Title
    estate: str
    forename: str
    surname: str

    status: int
    grip: int
    wealth: int

    # These apply modifiers to the Colonel's unit when he's with them
    steadiness: int

    traits: list[Trait]
    positions: list[Position]

    def __init__(self, faction):
        self.faction = faction
        self.grip = 4
        self.status = 3
        self.wealth = 0
        self.steadiness = 0
        self.traits = []

    def shortName(self) -> str:
        return f"{"Lord " if self.title >= Title.Baron else ""}{self.surname}"

    def fullName(self) -> str:
        return f"{self.preHonourific()}{self.forename} {self.surname}{self.postHonourific()}"

    def preHonourific(self) -> str:
        """ Titles which prefix the name like Sir """
        #TODO: how do clergy and judges work here?
        if self.title == Title.Commoner:
            return ""
        elif self.title in [Title.Knight, Title.Baronet]:
            return "Sir "
        return "Lord "   

    def postHonourific(self) -> str:
        """ Titles which postfix the name like MP"""
        if Position.MP in self.positions:
            return " MP"
        elif Position.JP in self.positions:
            return " JP"
        return ""
        
    def generateTraits(self, num: int) -> list[Trait]:
        """ Generate N suitable traits for this Colonel """
        indices = sample(range(0, 4), num)
        traits = []
        for index in indices:
            # Indices are in mutually incompatible pairs; randomly select one of them
            index = index * 2
            if randint(0,1) == 1:
                index = index + 1
            traits.append(Trait(index))
        return traits

    def applyTraits(self, traits: list[Trait]) -> None:
        """ Apply the effects of the given traits and store them for later"""
        for trait in traits:
            print(trait.name)
            match trait:
                case Trait.Sharp:
                    self.grip = self.grip + 1
                case Trait.Poltroon:
                    self.grip = self.grip - 1
                case Trait.Handsome:
                    self.status = self.status + 1
                case Trait.Unsightly:
                    self.status = self.status - 1
                case Trait.Wealthy:
                    self.wealth = self.wealth + drawSingle().value()
                case Trait.Dissolute:
                    self.wealth = max(0, self.wealth - drawSingle().value())
                case Trait.Stern:
                    self.steadiness = self.steadiness + 1
                case Trait.Fussy:
                    self.steadiness = self.steadiness - 1

        self.traits = self.traits + traits

    def generatePositions(self, num: int) -> list[Position]:
        """ Generate up to N suitable positions for this Colonel"""
        positions = []
        for i in range(num):
            # Peers can't be MPs, clergy etc
            if self.title >= Title.Baron:
                # Let's say 50% of peers have no other position
                if randint(0, 3) >= 2:
                    continue
                elif randint(0,1) == 1:
                    positions.append(Position.Governer)
                else:
                    positions.append(Position.Commander)
                continue
            # Let's say 25% of non-peers are plain country gentlemen
            if randint(0, 3) == 3:
                continue
            # Lots of Parliamentarian MPs
            if randint(0, 3) == 3:
                positions.append(Position.MP)
                continue
            # Otherwise look through the whole list in random order and pick the first which
            # for which we satisfy the prerequisites and which we don't already have
            positionIndices = [i for i in range(0, len(Position))]
            shuffle(positionIndices)
            for positionIndex in positionIndices:
                pos = Position(positionIndex)
                if positionPrerequisites[pos](self):
                    positions.append(pos)
                    break
        
        return positions

    def applyPositions(self, positions: list[Position]) -> None:
        for pos in positions:
            print(pos.name)
            match pos:
                case Position.Merchant:
                    self.wealth = self.wealth + drawSingle().value()
                case Position.JP:
                    self.steadiness = self.steadiness + 1
                case Position.MP:
                    self.status = self.status + 2
                case Position.Judge:
                    self.status = self.status + 1
                    self.steadiness = self.steadiness + 1
                case Position.Clergy:
                    self.status = self.status + 1
                    self.piety = self.piety + 2
                case Position.Governer:
                    self.status = self.status + 2
                    self.steadiness = self.steadiness + 1
                case Position.Commander:
                    self.status = self.status + 2
                    self.steadiness = self.steadiness + 1
                    self.grip = self.grip + 1

        self.positions = positions

def cardToRank(card: Card) -> Title:
    match card.rank():
        case Rank.King:
            return Title.Duke
        case Rank.Queen:
            return Title.Marquess
        case Rank.Jack:
            return Title.Earl
        case Rank.Ten:
            return Title.Viscount
        case Rank.Nine:
            return Title.Baron
        case Rank.Eight:
            return Title.Baronet
        case Rank.Seven | Rank.Six:
            return Title.Knight
        case _:
            return Title.Commoner

#TODO: pass in already-made player decisions via kwargs?
def generateColonel(faction: Faction) -> Colonel:
    col = Colonel(faction)

    # First, piety because it determines a lot 
    [pietyCard] = draw(2, 1) if faction == Faction.Parliamentarian else draw(1,1)
    col.piety = pietyCard.value()

    # Now rank. Royalists tend to be higher in rank, Puritans lower
    if col.piety == 10:
        [titleCard] = draw(2, 1, False)
    elif faction == Faction.Parliamentarian:
        [titleCard] = draw(1, 1)
    else:
        [titleCard] = draw(2, 1)

    col.title = cardToRank(titleCard)
    if col.title >= Title.Baron:
        col.estate = estates[randint(0,9)]
    
    # Now names: Piety 10 means a Pious Puritan, otherwise split choices between Salts of the Earth
    # and the two (for now) faction-specific names 50:50
    forenameTable = "salts"
    if col.piety == 10:
        forenameTable = "puritans"
    elif faction == Faction.Royalist and randint(0, 7) > col.title:
        forenameTable = "cavaliers"
    elif faction == Faction.Parliamentarian and randint(0, 7) > col.title:
        forenameTable = "parliamentarians"

    # Always pick both names either from the matching pair of tables or from Salts of the Earth
    surnameTable = "salts"
    if col.piety == 10:
        surnameTable = "puritans"
    elif faction == Faction.Royalist and randint(0, 5) > col.title:
        surnameTable = "cavaliers"
    elif faction == Faction.Parliamentarian and randint(0, 5) > col.title:
        surnameTable = "parliamentarians"

    col.forename = forenames[forenameTable][randint(0,9)]
    col.surname = surnames[forenameTable][randint(0,9)]

    # Now work out status, grip etc
    col.status = 3 + col.title # Title confers status!
    # Title also generally leads to wealth
    col.wealth = col.title + drawSingle().value()
    col.grip = 3 # however it does not make you a good soldier!

    col.applyTraits(col.generateTraits(2))
    col.applyPositions(col.generatePositions(1))
    return col