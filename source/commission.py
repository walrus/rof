""" Commission of Array: a pre-game Colonel generator for Regiment of Foote """

from source.cards import Card, draw, Rank
from random import randint

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


class Colonel:
    faction: Faction
    piety: int
    title: Title
    estate: str
    forename: str
    surname: str

    status: int
    grip: int
    courage: int
    wealth: int
    # traits: list[Trait] TODO personality traits

    def __init__(self, faction):
        self.faction = faction
        self.grip = 4
        self.status = 3

    def shortName(self) -> str:
        return f"{"Lord " if self.title >= Title.Baron else ""}{self.surname}"

    def fullName(self) -> str:
        return f"Name: {self.honourific()} {self.forename} {self.surname}"

    def honourific(self) -> str:
        # TODO update when I add things like MP?
        if self.title == Title.Commoner:
            return ""
        elif self.title in [Title.Knight, Title.Baronet]:
            return "Sir"
        return "Lord"   

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
def generate(faction: Faction) -> Colonel:
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

    print(f"Short name: {col.shortName()}")
    print(f"Full name:  {col.fullName()}, {col.title.name} {"of " if col.title >= Title.Baron else ""}{col.estate if col.title >= Title.Baron else ""}")

    return col