from source.cards import Card
from source.commission import Faction, generateColonel
from source.game import Game
from source.players import AIPlayer
from source.units import InfantryUnit

if __name__ == "__main__":
    # Play with two evenly matched units until someone runs away...again and again
    numGames = 100
    maxGameLength = 30

    royalistVictories = 0
    parliamentVictories = 0
    draws = 0

    turnsTaken = {}
    for i in range(1,maxGameLength):
        turnsTaken[i] = 0

    for gameIndex in range(numGames):
        print(f"Game {gameIndex}")
        col1 = generateColonel(Faction.Royalist)
        col1.grip = 4
        royalists = InfantryUnit(col1.shortName(), Faction.Royalist, 3, 3, (0, 50))
        # One lower point of steadiness than usual
        royalists.setSteadiness(Card.fromShortString("2♠")) # pyright: ignore[reportArgumentType]
        player1 = AIPlayer("Dave", Faction.Royalist, col1, royalists)
        print(f"Player Charles commands {royalists.name()}")

        col2 = generateColonel(Faction.Parliamentarian)
        col2.grip = 4
        parliamentarians = InfantryUnit(col2.shortName(), Faction.Parliamentarian, 3, 3, (0, 10))
        print(f"Player Oliver commands {parliamentarians.name()}")

        player2 = AIPlayer("Jim", Faction.Parliamentarian, col2, parliamentarians)

        game = Game([player1, player2])

        bothSidesFighting = True
        turnsElapsed = 1
        while bothSidesFighting and turnsElapsed < maxGameLength:
            game.play_turn()
            turnsElapsed = turnsElapsed + 1

            if not royalists.fitToFight() or not parliamentarians.fitToFight():
                bothSidesFighting = False

            if turnsElapsed % 10 == 0:
                print(f"{turnsElapsed} turns elapsed")

        turnsTaken[turnsElapsed] = turnsTaken[turnsElapsed] + 1

        if turnsElapsed == maxGameLength:
            print(f"Game {gameIndex} ended in a draw")
            draws = draws + 1
        else:
            victor = "Parliament" if parliamentarians.fitToFight() else "the Royalists"
            print(f"Game {gameIndex} ended after {turnsElapsed} turns; {victor} won")
            if victor == "Parliament":
                parliamentVictories = parliamentVictories + 1
            else:
                royalistVictories = royalistVictories + 1

    # Now we're done with all of the tests, show us the numbers!
    print(f"After {numGames} games, there are: ")
    print(f"    {royalistVictories} Royalist victories")
    print(f"    {parliamentVictories} Parliament victories")
    if draws > 0:
        print(f"    and {draws} draws")

    print("Turns elapsed: ")
    for turn, count in turnsTaken:
        print(f"{turn} turns: {count}")