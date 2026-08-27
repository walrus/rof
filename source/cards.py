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
class Card:
    index: int

    def __init__(self, index):
        self.index = index

    @classmethod
    def fromRankAndSuit(cls, rank: Rank, suit: Suit):
        return cls((rank * 4) + suit)

    def __str__(self):
        return f"The {self.rank().name} of {self.suit().name}"

    def suit(self) -> Suit:
        return Suit(self.index % 4)

    def rank(self) -> Rank:
        return Rank(self.index // 4)

    def value(self) -> int:
        return Values[self.index // 4]

    def __gt__(self, other):
        return self.index > other.index

    def __ge__(self, other):
        return self.index >= other.index

    def __lt__(self, other):
        return self.index < other.index

    def __le__(self, other):
            return self.index <= other.index
        
    def __eq__(self, value):
        return self.index == value.index

""" Draw N random cards from a standard 52-card deck """
def draw(num: int) -> list[Card]:
    if num > 51:
        return []
    
    indices = sample(range(0, 52), num)
    return [Card(index) for index in indices]

""" Sum the best N cards from the given set """
def sumBest(cards: list[Card], n: int) -> int:
    if n > len(cards):
        raise ValueError("Asked for too many cards!")
    elif n == len(cards):
        return sum(card.value() for card in cards)

    cards.sort(reverse=True)
    return sum(card.value() for card in islice(cards, n))

""" Number of cards in the set which are at or above the given threshold 
    E.G how many Jacks or higher?
""" 
def numAboveThreshold(cards: list[Card], threshold: Card) -> int:
    return sum(1 for card in cards if card >= threshold)