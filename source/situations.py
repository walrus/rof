from source.units import Unit, Outcome
from source.cards import draw, sumCards, numAboveThreshold, allAces, allFaceCards, numAces
from source import constants
""" For calculating what happens to one or more Units when they perform one or more Actions """

""" Monte Carlo simulate red shooting at blue
    For now, ignores cover etc """
def shootAt(red: Unit, blue: Unit, distance: int) -> tuple[Outcome, Outcome]:
    target = distance + blue.armour
    cards = draw(red.firepower(), constants.BEST_OF)

    casualties = sumCards(cards) // target
    blueDisorder = numAboveThreshold(cards, blue.steadiness)
    panic = blueDisorder >= constants.PANIC_THRESHOLD
    blueEvent = allFaceCards(cards)

    redDisorder = numAces(cards)
    redEvent = allAces(cards)

    redOutcome = Outcome(0, redDisorder, False, redEvent)
    blueOutcome = Outcome(casualties, blueDisorder, panic, blueEvent)

    return (redOutcome, blueOutcome)