from source.commission import Faction, generateColonel
from source.game import Game
from source.players import AIPlayer, HumanPlayer
from source.units import CavalryUnit, InfantryUnit

if __name__ == "__main__":
    # Play until someone runs away

    col1 = generateColonel(Faction.Royalist)
    cav = CavalryUnit(col1.shortName(), Faction.Royalist, 2, 4, (0, 50))
    player1 = AIPlayer("Dave", Faction.Royalist, col1, cav)
    print(f"Player Charles commands {cav.name()}")

    col2 = generateColonel(Faction.Parliamentarian)
    inf = InfantryUnit(col2.shortName(), Faction.Parliamentarian, 3, 3, (0, 10))
    player2 = HumanPlayer("Jim", Faction.Parliamentarian, col2, inf)
    print(f"Player Oliver commands {inf.name()}")

    game = Game([player1, player2])

    bothSidesFighting = True
    turns_elapsed = 0
    while bothSidesFighting:
        game.play_turn()
        turns_elapsed = turns_elapsed + 1
        if not cav.fitToFight() or not inf.fitToFight():
            bothSidesFighting = False

    print(f"Game ended after {turns_elapsed} turns")