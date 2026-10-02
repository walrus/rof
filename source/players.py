from source.cards import Card, draw, highestCombination
from source.units import Unit
from source.orders import Order, basicOrders
from source import constants

"""Represents the actual people playing the game, and their in-game Colonel"""

class Player:
    name: str
    grip: int # Hand size
    unit: Unit
    hand: list[Card]

    def __init__(self, name, grip, unit):
        self.name = name
        self.grip = grip
        self.unit = unit
        self.hand = draw(grip, grip)

    def orderOptions(self) -> list[Order]:
        highestCardCombo = highestCombination(self.hand)

        return [order for order in basicOrders if order.isPossible(highestCardCombo, self.unit)]