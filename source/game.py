import logging

from source.players import Player, AIPlayer
from source.units import Unit
from source.jev import chooseActivationCardsForPlayers

logger = logging.getLogger(__name__)

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
        activationCards = []
        playerHandsForJev = {}
        aiPlayers = {}
        for player in self.players: # type: ignore
            player.drawStep()
            logger.info(f"Player {player.name} has hand {' '.join(str(card) for card in player.hand)}")
            
            if isinstance(player, AIPlayer):
                playerHandsForJev[player.name] = player.hand
                aiPlayers[player.name] = player
            else:
                card = player.chooseActivationCard()
                activationCards.append((card, player))
                print(player.unit.status())

        # Choose activation cards in parallel for speed
        if playerHandsForJev:
            # TODO: ew.
            chosenCards = chooseActivationCardsForPlayers(playerHandsForJev)
            activationCards.extend([(card, aiPlayers[player]) for player, card in chosenCards.items()])

        activationCards.sort(key= lambda x: x[0], reverse=True) # sort by the card not the player

        # Activation phase
        for card, player in activationCards:
            logger.warning(f"Activation: {player.name} with a {card!s}")
            enemyUnits = [unit for unit in self.units if unit.isEnemy(player.faction)]
            order = player.chooseOrder(enemyUnits)
            player.unit.carryOut(order)
            logger.info(f"{player.unit.name()} now at {player.unit.position[0]},{player.unit.position[1]}")
            logger.info(f"{player.unit.name()} now has {player.unit.disorder} disorder; status {player.unit.morale}")
        
        # Panic phase
        #TODO: figure out how I'm checking for panic here
        for player in self.players:
            player.enforceHandSize()

    def play(self):
        pass