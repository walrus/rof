""" Just misc bits from the scratchpad that I didn't want to delete"""

from source.cards import (
    Card,
    Rank,
    Suit,
    combinations,
    draw,
    highestCombination,
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
            print(f"Done {i}")

    print("### RESULTS ###")
    print("Sums: ")
    for value, count in sums.items():
        print(f"{value}, {count}")

    print()
    print("Thresholds: ")
    for value, count in thresholds.items():
        print(f"{value}, {count}")

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
            print(f"Done {i}")

    print("### RESULTS ###")
    print("Highest Combinations: ")
    for value, count in combinations.items():
        print(f"{value}, {count}")

def showCombinations():
    
    cards = draw(4,4)
    handStr = ' '.join([str(card) for card in cards])
    print(f"Hand: {handStr}")
    
    combos = combinations(cards)

    for val, cardList in combos:
        cardStr = ' '.join([str(card) for card in cardList])
        print(f"Val: {val}, cards: {cardStr}")

def testPanicOptions():
    """ Test 2-card draw """
    disorder = {}

    ace = Card.fromRankAndSuit(Rank.Two, Suit.Clubs)
    king = Card.fromRankAndSuit(Rank.King, Suit.Clubs)
        
    print("Computing...")
    for i in range(21):
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
        print(f"{value}, {count / 1000000}")

