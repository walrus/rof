# Demonstrate three different ways of figuring out how Orders should work
from source.cards import draw, highestCombination, highestValue, sumCards


def monteCarlo1(iterations: int) -> dict[int, int]:
    # Option 1: Single Card
    sums = {}
    for i in range(1,11):
        sums[i] = 0

    for i in range(iterations):
        cards = draw(4, 4) # draw 4 cards, keep 4

        highest = highestValue(cards)
        sums[highest] = sums[highest] + 1

    return sums

def monteCarlo2(iterations: int) -> dict[int, int]:
    # Option 2: Sum of all cards in hand
    sums = {}
    for i in range(4,41):
        sums[i] = 0

    for i in range(iterations):
        cards = draw(4, 4) # draw 4 cards, keep 4

        totalValue = sumCards(cards)
        sums[totalValue] = sums[totalValue] + 1

    return sums

def monteCarlo3(iterations: int) -> dict[int, int]:
    # Option 3: Sum of all cards of same suit in hand
    sums = {}
    for i in range(1,41):
        sums[i] = 0

    for i in range(iterations):
        cards = draw(4, 4)

        totalValue = highestCombination(cards)
        sums[totalValue] = sums[totalValue] + 1

    return sums

def showResults(iterations: int, results: dict[int, int]) -> None:
    print(f"Results for {iterations} iterations")
    for value, count in results.items():
        if count > 0:
            print(f"{value}, {count}")

if __name__ == "__main__":
    numIterations = 100000

    singleCardResults = monteCarlo1(numIterations)
    allCardResults = monteCarlo2(numIterations)
    sameSuitResults = monteCarlo3(numIterations)

    print("Option 1: Single card")
    showResults(numIterations, singleCardResults)
    print()

    print("Option 2: Sum of all cards")
    showResults(numIterations, allCardResults)
    print()

    print("Option 2: Sum of all cards of same suit")
    showResults(numIterations, sameSuitResults)
    print()
    