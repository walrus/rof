from source.cards import Card, draw, highestCombination, combinations
from source.units import Unit, Order, basicOrders
from source import constants

from source.commission import Colonel

from random import choice
from typing import Optional

"""Represents the actual people playing the game"""

class Player:
    name: str
    unit: Unit
    colonel: Colonel
    hand: list[Card]

    def __init__(self, name, colonel, unit):
        self.name = name
        self.colonel = colonel
        self.unit = unit
        self.hand = draw(colonel.grip, colonel.grip)

    @property
    def grip(self):
        return self.colonel.grip

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
        """ Get all possible Orders, ruling out any that no combination of cards in hand can play"""
        highestCardCombo = highestCombination(self.hand)
        print(f"Highest combo: {highestCardCombo}")
        return [order for order in basicOrders if order.isPossible(highestCardCombo, self.unit)]

    def chooseOrder(self) -> Optional[Order]:
        """ Pick an order to give """
        #TODO take account of cards used & actually pick orders sensibly!
        cardCombos = combinations(self.hand)
        options = self.orderOptions()

        if not options:
            print("No options available!")
            return None

        return choice(self.orderOptions())