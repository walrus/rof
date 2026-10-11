""" Calls Jev to make simulated player decisions """
from json import dumps, loads

from typesafe_sdk import Choice, TypeSafeClient

from source.cards import Card
from source.units import Order, Unit


def unitStateToDict(unit: Unit) -> dict[str, str]:
    """ Write current Unit state to a dict for adding further info"""
    state = {}
    state['name'] = unit.name()
    state['currentOrder'] = unit.currentOrder.name if unit.currentOrder else 'None'
    state['morale'] = str(unit.morale)
    state['fighting'] = str(unit.fighting)
    state['shooting'] = str(unit.shooting)
    state['disorder'] = str(unit.disorder)
    state['strength'] = str(unit.strength())
    return state

def unitStateToJson(unit: Unit) -> str:
    """ Turn Unit state into something Jev can understand """
    return dumps(unitStateToDict(unit))


def chooseActivationCard(cards : list[Card]) -> Card:
    """ Ask Jev to choose a card from hand to use for activation"""
    # We don't need the value part of the dict for this query, but Jev requires it as a dict
    cardDict = {str(card): None for card in cards}
    with TypeSafeClient() as client:
        response = client.system_one(
            state={"document": "I'm playing a game. As part of this game I need to pick a card from the given hand. "
            "Higher cards are better, but if I have cards from the same suit I want to save them for other things. Aces are low"},
            questions={
                "card": Choice(
                    instructions="Which card should I choose?",
                    criteria=cardDict,
                ),
            },
        )
        cardChoice = response.answers["card"]
        if cardChoice:
            card = Card.fromShortString(cardChoice.choice) # pyright: ignore[reportAttributeAccessIssue]
            if card:
                return card
            # Otherwise it failed to parse for some reason; fall back to the first card in the list
    
    # Fallback if I've messed up somewhere
    print(f"Something went wrong choosing an activation card; defaulting to {cards[0]}")
    return cards[0]

def chooseCardToDiscard(cards : list[Card]) -> Card:
    """ Ask Jev to choose a card from hand to discard"""
    # We don't need the value part of the dict for this query, but Jev requires it as a dict
    cardDict = {str(card): None for card in cards}
    with TypeSafeClient() as client:
        response = client.system_one(
            state={"document": "I'm playing a game in which I have a hand of cards, and right now I need to pick the least-useful card to discard. "
            "Higher cards are better, and having multiple cards of the same suit is even better (as long as their values sum to more than 10) "
            "Aces are worth 1, number cards are worth their number, and other face cards are worth 10"},
            questions={
                "card": Choice(
                    instructions="Which card should I discard?",
                    criteria=cardDict,
                ),
            },
        )
        cardChoice = response.answers["card"]
        if cardChoice:
            card = Card.fromShortString(cardChoice.choice) # pyright: ignore[reportAttributeAccessIssue]
            if card:
                return card
            # Otherwise it failed to parse for some reason; fall back to the first card in the list
    
    # Fallback if I've messed up somewhere
    print(f"Something went wrong discarding; defaulting to {cards[0]}")
    return cards[0]

def chooseOrder(unit : Unit, enemies : list[Unit], orders : dict[str, Order], cardCombos: list[tuple[int, list[Card]]]) -> tuple[Order | None, list[Card]]:
    """ Ask Jev to choose an order to give and the cards to discard in order to play it
        Makes two calls to the Jev API so that we can ensure the cards are actually capable of playing the Order"""

    # Turn our lists of orders and cards into dicts of JSON objects that Jev can understand
    cardOptions = {}

    for i, combo in enumerate(cardCombos):
        optionDict = {
            'cards': [str(card) for card in combo[1]],
            'value': str(combo[0])
        }
        cardOptions[str(i)] = dumps(optionDict)

    # It's always an option to simply do nothing, but we represent that in the game engine with None
    orderOptions = {}
    nothingOrderDict = {
        'description': "Carry on without giving any new orders this Turn",
        'difficulty': 0
    }
    orderOptions['Nothing'] = dumps(nothingOrderDict)

    for name, order in orders.items():
        orderDict = {
            'description': order.description,
            'difficulty': str(order.currentDifficulty(unit))
        }
        orderOptions[name] = dumps(orderDict)

    unitState = unitStateToJson(unit)

    enemyState = {}
    for enemy in enemies:
        enemyDict = unitStateToDict(enemy)
        
        enemyDict['distance'] = str(unit.distanceTo(enemy))
        enemyDict['isInRange'] = str(unit.inRange(enemy))

        enemyState[enemy.name()] = dumps(enemyDict)

    orderToReturn = None
    cardChoiceToReturn = []

    with TypeSafeClient() as client:
        response = client.system_one(
            state={"document": "I'm playing a game in which I have a hand of cards, and right now I need to pick a combination of cards to play an Order. "
            "I need to decide on an Order to play, taking into account `unitState` and `enemyState`, but I should try not to waste good cards."
            "Higher cards are better, and having multiple cards of the same suit is even better (as long as their values sum to more than 10) "
            "Aces are worth 1, number cards are worth their number, and other face cards are worth 10",
            "unitState": unitState,
            "enemyState": enemyState
            },
            questions={
                "order": Choice(
                    instructions="Which Order should I play this turn? Take `unitState` into account",
                    criteria=orderOptions
                ),
            },
        )
        orderChoice = response.answers["order"]
        if orderChoice and orderChoice.choice and orderChoice.choice != "Nothing": # pyright: ignore[reportAttributeAccessIssue]
            orderToReturn = orders[orderChoice.choice] # pyright: ignore[reportAttributeAccessIssue]

    # If we're not giving an Order, then early out
    if not orderToReturn:
        return None, []

    # Otherwise, now we have an order, choose the cards to play it

    with TypeSafeClient() as client:
        response = client.system_one(
            state={"document": "]I need to pick a combination of cards with a `value` at least as high as `orderDifficulty` but ideally only just as high, so I can save better cards for later."
            "Higher cards are better, and having multiple cards of the same suit is even better (as long as their values sum to more than 10) "
            "Aces are worth 1, number cards are worth their number, and other face cards are worth 10",
            "orderDifficulty": str(orderToReturn.currentDifficulty(unit)),
            },
            questions={
                "cards": Choice(
                    instructions="Which cards should I use to play the Order? " \
                    "Try to play the combination of cards with the lowest possible Value which meets or exceeds `orderDifficulty`" \
                    "If `orderDifficulty` is 0, then play no cards (the empty list)",
                    criteria=cardOptions,
                ),
            },
        )

        cardChoice = response.answers["cards"]
        if cardChoice and cardChoice.choice: # pyright: ignore[reportAttributeAccessIssue]
            cardsFromChoice = loads(cardOptions[cardChoice.choice])['cards'] # pyright: ignore[reportAttributeAccessIssue]
            cardChoiceToReturn = [Card.fromShortString(card) for card in cardsFromChoice]

    return orderToReturn, cardChoiceToReturn # pyright: ignore[reportReturnType] (fromShortString won't fail)