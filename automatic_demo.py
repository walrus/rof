import logging

from source.cards import Card
from source.commission import Faction, generateColonel
from source.game import Game
from source.players import AIPlayer
from source.units import InfantryUnit

# Only log big events for this demo
logging.basicConfig(level=logging.ERROR, format="%(message)s")
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Play with two evenly matched units until someone runs away...again and again
    numGames = 100
    maxGameLength = 30

    royalistVictories = 0
    parliamentVictories = 0
    draws = 0

    turnsTaken = {}
    for i in range(1,maxGameLength + 1):
        turnsTaken[i] = 0

    for gameIndex in range(numGames):
        logger.error(f"Game {gameIndex}")
        col1 = generateColonel(Faction.Royalist)
        col1.grip = 4
        royalists = InfantryUnit(col1.shortName(), Faction.Royalist, 3, 3, (0, 50))
        # One lower point of steadiness than usual
        royalists.setSteadiness(Card.fromShortString("2♠")) # pyright: ignore[reportArgumentType]
        player1 = AIPlayer("Dave", Faction.Royalist, col1, royalists)
        logger.error(f"Player Charles commands {royalists.name()}")

        col2 = generateColonel(Faction.Parliamentarian)
        col2.grip = 4
        parliamentarians = InfantryUnit(col2.shortName(), Faction.Parliamentarian, 3, 3, (0, 10))
        logger.error(f"Player Oliver commands {parliamentarians.name()}")

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
                logger.error(f"{turnsElapsed} turns elapsed")

        turnsTaken[turnsElapsed] = turnsTaken[turnsElapsed] + 1

        if turnsElapsed == maxGameLength:
            logger.error(f"Game {gameIndex} ended in a draw")
            draws = draws + 1
        else:
            victor = "Parliament" if parliamentarians.fitToFight() else "the Royalists"
            logger.error(f"Game {gameIndex} ended after {turnsElapsed} turns; {victor} won")
            if victor == "Parliament":
                parliamentVictories = parliamentVictories + 1
            else:
                royalistVictories = royalistVictories + 1

    # Now we're done with all of the tests, show us the numbers!
    logger.error(f"After {numGames} games, there are: ")
    logger.error(f"    {royalistVictories} Royalist victories")
    logger.error(f"    {parliamentVictories} Parliament victories")
    if draws > 0:
        logger.error(f"    and {draws} draws")

    logger.error("Turns elapsed: ")
    for turn, count in turnsTaken:
        logger.error(f"{turn} turns: {count}")