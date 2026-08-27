from enum import IntEnum
from random import sample
from itertools import islice

""" Utilities for card distribution """

class Suit(IntEnum):
    Clubs = 0
    Diamonds = 1
    Hearts = 2
    Spades = 3

class Rank(IntEnum):
    Ace = 0
    Two = 1
    Three = 2
    Four = 3
    Five = 4
    Six = 5
    Seven = 6
    Eight = 7
    Nine = 8
    Ten = 9
    Jack = 10
    Queen = 11
    King = 12

""" Used when summing cards """
Values = {
    0: 1,
    1: 2,
    2: 3,
    3: 4,
    4: 5,
    5: 6,
    6: 7,
    7: 8,
    8: 9,
    9: 10,
    10: 10, # Jack
    11: 10, # Queen
    12: 10, # King
}

# For printing card short names E.G 5♠
suitSymbols = {
    Suit.Clubs:    "♣",
    Suit.Diamonds: "♦",
    Suit.Hearts:   "♥",
    Suit.Spades:   "♠"
}

rankLetters = {
    Rank.Ace:   "A",
    Rank.Two:   "2",
    Rank.Three: "3",
    Rank.Four:  "4",
    Rank.Five:  "5",
    Rank.Six :  "6",
    Rank.Seven: "7",
    Rank.Eight: "8",
    Rank.Nine:  "9",
    Rank.Ten:   "10",
    Rank.Jack:  "J",
    Rank.Queen: "Q",
    Rank.King:  "K"
}

class Card:
    index: int

    def __init__(self, index):
        self.index = index

    @classmethod
    def fromRankAndSuit(cls, rank: Rank, suit: Suit):
        return cls((rank * 4) + suit)

    def __str__(self):
        return f"{rankLetters[self.rank()]}{suitSymbols[self.suit()]}"

    def fullName(self):
        return f"The {self.rank().name} of {self.suit().name}"

    def suit(self) -> Suit:
        return Suit(self.index % 4)

    def rank(self) -> Rank:
        return Rank(self.index // 4)

    def value(self) -> int:
        return Values[self.index // 4]

    def __gt__(self, other):
        return self.index > other

    def __ge__(self, other):
        return self.index >= other

    def __lt__(self, other):
        return self.index < other

    def __le__(self, other):
        return self.index <= other
        
    def __eq__(self, value):
        return self.index == value

""" Draw N random cards from a standard 52-card deck, keeping some"""
def draw(num: int, keep: int) -> list[Card]:
    if num > 51 or keep > num:
        return []
    
    indices = sample(range(0, 52), num)
    cards = [Card(index) for index in indices]

    print("Draw: ")
    for c in cards:
        print(f"    {c}")
    

    if (num == keep):
        return cards

    cards.sort(reverse=True)
    kc = cards[:keep]

    print("Keep: ")
    for c in kc:
        print(f"    {c}")
    
    return kc

""" Sum the values of the given cards"""
def sumCards(cards: list[Card]) -> int:
    return sum(card.value() for card in cards)

""" Number of cards in the set which are at or above the given threshold 
    E.G how many Jacks or higher?
""" 
def numAboveThreshold(cards: list[Card], threshold: Card) -> int:
    return sum(1 for card in cards if card >= threshold)

def allAces(cards: list[Card]) -> bool:
    return all(card.rank() == Rank.Ace for card in cards)

def allFaceCards(cards: list[Card]) -> bool:
    return all (card.rank() >= Rank.Jack for card in cards)