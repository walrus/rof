from units import Unit
from cards import draw, sumCards, numAboveThreshold, allAces, allFaceCards
import constants
""" For calculating what happens to one or more Units when they perform one or more Actions """

""" Describes the change in state of a Unit after an Action """
class Outcome:
    casualties: int
    disorder: int
    panic: bool
    event: bool # TODO: work out how to encode the events table

    def __init__(self, casualties, disorder, panic, event) -> None:
        self.casualties = casualties
        self.disorder = disorder
        self.panic = panic
        self.event = event

""" Monte Carlo simulate red shooting at blue
    For now, ignores cover etc """
def shootAt(red: Unit, blue: Unit, distance: int) -> tuple[Outcome, Outcome]:
    target = distance + blue.armour
    cards = draw(red.firepower(), constants.BEST_OF)

    casualties = sumCards(cards) // target
    disorder = numAboveThreshold(cards, blue.steadiness)
    panic = disorder >= constants.PANIC_THRESHOLD
    redEvent = allAces(cards)
    blueEvent = allFaceCards(cards)

    redOutcome = Outcome(0, 0, False, redEvent)
    blueOutcome = Outcome(casualties, disorder, panic, blueEvent)

    return (redOutcome, blueOutcome)