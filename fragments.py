""" Just misc bits from the scratchpad that I didn't want to delete"""

from source.cards import (
    Card,
    Rank,
    Suit,
    combinations,
    draw,
    numAboveThreshold,
    sumCards,
)


def monteCarloDraw():
    # Monte carlo simulate a bunch of card draws

    sums = {}
    for i in range(3,31):
        sums[i] = 0

    thresholds = {}
    for i in range(4):
        thresholds[i] = 0

    for i in range(10000000):
        cards = draw(4, 3)

        sum = sumCards(cards)
        sums[sum] = sums[sum] + 1

        jack = Card.fromRankAndSuit(Rank.Jack, Suit.Clubs)
        threshold = numAboveThreshold(cards, jack)
        thresholds[threshold] = thresholds[threshold] + 1

        if (i % 10000 == 0):
            print(f"Done {str(i)}")

    print("### RESULTS ###")
    print("Sums: ")
    for value, count in sums.items():
        print(f"{str(value)}, {count}")

    print()
    print("Thresholds: ")
    for value, count in thresholds.items():
        print(f"{str(value)}, {count}")

def monteCarloHighestSum():
    """ Useful for working out what Orders a hand can give you"""
    combinations = {}
    for i in range(1,51):
        combinations[i] = 0

    for i in range(10000000):
        # I think default hand size is probably 4
        cards = draw(5, 5)
        highest = highestCombination(cards)
        
        combinations[highest] = combinations[highest] + 1

        if (i % 10000 == 0):
            print(f"Done {str(i)}")

    print("### RESULTS ###")
    print("Highest Combinations: ")
    for value, count in combinations.items():
        print(f"{str(value)}, {count}")

def showCombinations():
    
    cards = draw(4,4)
    handStr = ' '.join([str(card) for card in cards])
    print(f"Hand: {handStr}")
    
    combos = combinations(cards)

    for val, cardList in combos:
        cardStr = ' '.join([str(card) for card in cardList])
        print(f"Val: {str(val)}, cards: {cardStr}")

def testPanicOptions():
    """ Test 2-card draw vs one card plus Steadiness """
    disorder = {}
    steadiness = 7

    ace = Card.fromRankAndSuit(Rank.Two, Suit.Clubs)
    king = Card.fromRankAndSuit(Rank.King, Suit.Clubs)
        
    print("Computing...")
    for i in range(0,21):
        disorder[i] = 0

        for j in range(1000000):
            cards = draw(2, 2)
            sum = sumCards(cards)

            # Double aces always fail; double kings always succeed
            if numAboveThreshold(cards, ace) == 0:
                continue

            if sum >= i or numAboveThreshold(cards, king) == 2:
                disorder[i] = disorder[i] + 1

    print("### RESULTS ###")
    print("Sums: ")
    for value, count in disorder.items():
        print(f"{str(value)}, {count / 1000000}")

def simpleFirefight():
    red = InfantryUnit("Red", 12, 24)
    red.setSteadiness(Card.fromRankAndSuit(Rank.Jack, Suit.Clubs))
    blue = InfantryUnit("Blue", 12, 24)
    blue.setSteadiness(Card.fromRankAndSuit(Rank.Jack, Suit.Clubs))

    turnsOfShooting = 0

    while red.fitToFight() and blue.fitToFight():
        # randomise the order each turn
        redCard, blueCard = draw(2,2)

        turnsOfShooting = turnsOfShooting + 1

        if redCard > blueCard:
            print("Red shoots at Blue from 8 inches away")
            redOutcome, blueOutcome = shootAt(red, blue, 8)

            red.applyOutcome(redOutcome)
            blue.applyOutcome(blueOutcome)
            print(f"Blue strength now {blue.pike} pike and {blue.shot} shot; disorder {blue.disorder}")
            if not blue.fitToFight():
                break
            print("Blue returns fire from 8 inches away")
            blueOutcome, redOutcome = shootAt(blue, red, 8)

            red.applyOutcome(redOutcome)
            blue.applyOutcome(blueOutcome)
            print(f"Red strength now {red.pike} pike and {red.shot} shot; disorder {red.disorder}")
        else:
            print(" Blue shoots at Red from 8 inches away")
            blueOutcome, redOutcome = shootAt(blue, red, 8)
            red.applyOutcome(redOutcome)
            blue.applyOutcome(blueOutcome)

            if not red.fitToFight():
                break
            print("Red returns fire from 8 inches away")
            redOutcome, blueOutcome = shootAt(red, blue, 8)
            red.applyOutcome(redOutcome)
            blue.applyOutcome(blueOutcome)
        print()

    winner = "Red" if red.fitToFight() else "Blue"
    print(f"Exchange of fire ended after {turnsOfShooting} rounds. Winner {winner}")

    print(f"Red strength now {red.pike} pike and {red.shot} shot; disorder {red.disorder}")
    print(f"Blue strength now {blue.pike} pike and {blue.shot} shot; disorder {blue.disorder}")
