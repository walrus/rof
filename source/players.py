from source.cards import Card, draw, highestCombination
from source.units import Unit, Order, basicOrders
from source import constants

from random import choice

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

    def drawStep(self) -> None:
        self.hand.extend(draw(2,2))

    def enforceHandSize(self) -> None:
        if len(self.hand) <= self.grip:
            return

        # Otherwise got to get rid of some
        #TODO: do this somewhat more optimally!
        while len(self.hand) > self.grip:
            self.hand.pop()

    def chooseActivationCard(self) -> Card:
        """ Pick and spend an activation card """
        #TODO this more optimally
        return self.hand.pop()

    def orderOptions(self) -> list[Order]:
        highestCardCombo = highestCombination(self.hand)

        return [order for order in basicOrders if order.isPossible(highestCardCombo, self.unit)]

    def chooseOrder(self):
        """ Pick an order to give """
        #TODO take account of cards used
        #TODO actually pick orders sensibly!
        return =choice(self.orderOptions())