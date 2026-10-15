import logging

from source.commission import Faction, generateColonel
from source.game import Game
from source.players import AIPlayer, HumanPlayer
from source.units import CavalryUnit, InfantryUnit

# Only log decisions and major events for the demo, not minutiae
logging.basicConfig(level=logging.WARNING, format="%(message)s")
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Play until someone runs away

    col1 = generateColonel(Faction.Royalist)
    royalists = CavalryUnit(col1.shortName(), Faction.Royalist, 2, 4, (0, 50))
    player1 = AIPlayer("Charles", Faction.Royalist, col1, royalists)
    print(f"Player Charles commands {royalists.name()}")

    col2 = generateColonel(Faction.Parliamentarian)
    parliamentarians = InfantryUnit(col2.shortName(), Faction.Parliamentarian, 3, 3, (0, 10))
    player2 = HumanPlayer("Oliver", Faction.Parliamentarian, col2, parliamentarians)
    print(f"Player Oliver commands {parliamentarians.name()}")

    game = Game([player1, player2])

    bothSidesFighting = True
    turnsElapsed = 0
    while bothSidesFighting:
        turnsElapsed = turnsElapsed + 1
        print(f"Turn {turnsElapsed} \n")

        game.play_turn()

        if not royalists.fitToFight() or not parliamentarians.fitToFight():
            bothSidesFighting = False

    print(f"Game ended after {turnsElapsed} turns")
    victor = "Parliament" if parliamentarians.fitToFight() else "Royalists"
    print(f"The winner was {victor}")