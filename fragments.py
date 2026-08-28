""" Just misc bits from the scratchpad that I didn't want to delete"""

from source.cards import draw, sumCards, Card, numAboveThreshold, Rank, Suit

def monteCarloDraw():
    # Monte carlo simulate 10,000,000 draws

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

