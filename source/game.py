from source.players import Player
from source.units import Unit

""" Wrap the various objects up into a game """


class Game:
    players: list[Player]
    units: list[Unit]

    def __init__(self, players):
        self.players = players
        self.units = [player.unit for player in players]
        #TODO: more setup?

    def play_turn(self):
        """ Play a single Turn from start to finish"""

        # Draw Phase
        activation_cards = []
        for player in self.players: # type: ignore
            player.drawStep()
            #print(f"Player {player.name} has hand {' '.join(str(card) for card in player.hand)}")
            card = player.chooseActivationCard()
            activation_cards.append((card, player))

        activation_cards.sort(key= lambda x: x[0], reverse=True) # sort by the card not the player

        # Activation phase
        for card, player in activation_cards:
            #print(f"Activation: {player.name} with a {card!s}")
            enemyUnits = [unit for unit in self.units if unit.isEnemy(player.faction)]
            order = player.chooseOrder(enemyUnits)
            #print(f"Order: {player.unit.name()} is ordered to {order.name if order else "do nothing"}")
            player.unit.carryOut(order)
            #print(f"{player.unit.name()} now at {player.unit.position[0]},{player.unit.position[1]}")
            print(f"{player.unit.name()} now has {player.unit.disorder} disorder; status {player.unit.morale}")
        # Panic phase
        #TODO: figure out how I'm checking for panic here
        for player in self.players:
            player.enforceHandSize()

    def play(self):
        pass