"""Represents the actual people playing the game"""

from random import choice

from source.cards import Card, draw, highestCombination
from source.commission import Colonel
from source.jev import chooseActivationCard, chooseCardToDiscard
from source.units import Order, Unit, basicOrders


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

        # Otherwise got to get rid of some - most of the time this will be only one
        # but it's possible to E.G lose more than one Grip in a turn
        while len(self.hand) > self.grip:
            cardChoice = chooseCardToDiscard(self.hand)
            print(f"{self.name} chooses to discard a {cardChoice!s}")
            self.hand.remove(cardChoice)

    def chooseActivationCard(self) -> Card:
        """ Pick and spend an activation card, using Jev to choose """
        cardChoice = chooseActivationCard(self.hand)
        self.hand.remove(cardChoice)
        return cardChoice

    def orderOptions(self) -> list[Order]:
        """ Get all possible Orders, ruling out any that no combination of cards in hand can play"""
        highestCardCombo = highestCombination(self.hand)
        return [order for order in basicOrders if order.isPossible(highestCardCombo, self.unit)]

    def chooseOrder(self) -> Order | None:
        """ Pick an order to give """
        #TODO take account of cards used & actually pick orders sensibly!
        # cardCombos = combinations(self.hand)
        options = self.orderOptions()

        if not options:
            print("No options available!")
            return None

        return choice(self.orderOptions())