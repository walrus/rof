from source.players import Player

""" Wrap the various objects up into a game """


class Game:
    players = list[Player]

    def __init__(self, players):
        self.players = players
        #TODO: more setup?

    def play_turn(self):
        """ Play a single Turn from start to finish"""

        # Draw Phase
        activation_cards = []
        for player in self.players: # type: ignore
            player.drawStep()
            card = player.chooseActivationCard()
            print(f"{player.name} chooses to activate with a {card!s}")
            activation_cards.append((card, player))
        activation_cards.sort(key= lambda x: x[0], reverse=True) # sort by the card not the player

        # Activation phase
        for card, player in activation_cards:
            
            print(f"Activation: {player.name} with a {card!s}")
            order = player.chooseOrder()
            print(f"Order: {player.unit.name()} is ordered to {order.name if order else "do nothing"}")
            player.unit.carryOut(order)

        # Panic phase
        #TODO: figure out how I'm checking for panic here
        for player in self.players: # type: ignore
            player.enforceHandSize()

    def play(self):
        pass