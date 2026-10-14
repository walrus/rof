""" Calls Jev to make simulated player decisions """
import logging
from json import dumps, loads

from typesafe_sdk import Choice, TypeSafeClient

from source.cards import Card
from source.units import Order, Unit

logger = logging.getLogger(__name__)

def unitStateToDict(unit: Unit) -> dict[str, str]:
    """ Write current Unit state to a dict for adding further info"""
    state = {}
    state['name'] = unit.name()
    state['unitType'] = str(unit.unitType)
    state['currentOrder'] = unit.currentOrder.name if unit.currentOrder else 'None'
    state['morale'] = str(unit.morale)
    state['fighting'] = str(unit.fighting)
    state['shooting'] = str(unit.shooting)
    state['disorder'] = str(unit.disorder)
    state['firepower'] = str(unit.firepower)
    state['ferocity'] = str(unit.ferocity)
    state['position'] = f"{unit.position[0]},{unit.position[1]}"
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
    logger.info(f"Something went wrong choosing an activation card; defaulting to {cards[0]}")
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
    logger.info(f"Something went wrong discarding; defaulting to {cards[0]}")
    return cards[0]

def chooseOrder(unit : Unit, enemies : list[Unit], orders : dict[str, Order | None], cardCombos: list[tuple[int, list[Card]]]) -> tuple[Order | None, list[Card]]:
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
            'description': order.description if order else "None",
            'difficulty': str(order.currentDifficulty(unit) if order else 0)
        }
        orderOptions[name] = dumps(orderDict)

    unitState = unitStateToJson(unit)

    enemyState = {}
    for enemy in enemies:
        enemyDict = unitStateToDict(enemy)
        
        enemyDict['distance'] = str(unit.distanceTo(enemy))
        enemyDict['isInRange'] = str(unit.inRange(enemy))
        enemyDict['isInChargeRange'] = str(unit.inChargeRange(enemy))

        enemyState[enemy.name()] = dumps(enemyDict)

    orderToReturn = None
    cardChoiceToReturn = []

    with TypeSafeClient() as client:
        response = client.system_one(
            state={"document": "I'm playing a game in which I command a unit of troops. I need to decide which order to give them, "
            "based on both the unit's current state (`unitState`) and the state of any nearby enemies `enemyState`"
            "Broadly, the priority is to Rally the unit if it's Wavering or Panicked, fire on the enemy if in range and the unit isn't already firing, "
            "or Run/Move towards them if not in range. If the enemy unit is closer than 10 and they're wavering, we should Charge."
            "If the current Order matches what we would otherwise prioritise, consider `Encourage` if we have any Disorder or `Nothing`"
            "Cavalry units (`unitType` Cavalry) should prioritise charging the enemy if `isInChargeRange`, or move towards them otherwise",
            "unitState": unitState,
            "enemyState": enemyState
            },
            questions={
                "order": Choice(
                    instructions="Which Order should I play this turn? Take `unitState` and `enemyState` into account",
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
            "unitState": unitState
            },
            questions={
                "cards": Choice(
                    instructions="Which cards should I use to play the Order? " \
                    "Try to play the combination of cards with the lowest possible Value which meets or exceeds `orderDifficulty`," \
                    "except when the order is 'Encourage' - in which case if we have lots of `disorder` then play multiple cards if possible" \
                    "If `orderDifficulty` is 0, then play no cards (the empty list)",
                    criteria=cardOptions,
                ),
            },
        )

        cardChoice = response.answers["cards"]
        if cardChoice and cardChoice.choice: # pyright: ignore[reportAttributeAccessIssue]
            cardsFromChoice = loads(cardOptions[cardChoice.choice])['cards'] # pyright: ignore[reportAttributeAccessIssue]
            cardChoiceToReturn = [Card.fromShortString(card) for card in cardsFromChoice]

    # This is a fallback if I've messed up somewhere
    if not orderToReturn or not cardChoiceToReturn:
        logger.info("Something went choosing an Order; defaulting to Nothing")

    return orderToReturn, cardChoiceToReturn # pyright: ignore[reportReturnType] (fromShortString won't fail)

def chooseDieToLose(unit: Unit) -> bool:
    # Choose whether to discard a Firepower die (true) or a Ferocity die (false)
    unitState = unitStateToJson(unit)
    options = {
        'Firepower': None,
        'Ferocity': None
    }
    with TypeSafeClient() as client:
            response = client.system_one(
                state={"document": "I'm playing a game. As part of this game my unit of soldiers has taken casualties and needs to discard either a `Ferocity` or `Firepower` die"
                "I need to pick one, based on the following criteria: You can only reduce the `firepower` or `ferocity` stat (in `unitState`) to 0 if there are no other options. "
                "Cavalry rely on their Ferocity more; infantry on their Firepower, so pick the other die. If in doubt, reduce the higher one",
                "unitState": unitState,
                },
                questions={
                    "dice": Choice(
                        instructions="Which die should I discard?",
                        criteria=options,
                    ),
                },
            )
            diceChoice = response.answers["dice"]
            if diceChoice and diceChoice.choice: # pyright: ignore[reportAttributeAccessIssue]
                return diceChoice.choice == 'Firepower' # pyright: ignore[reportAttributeAccessIssue]
    
    # Fallback if I've messed up somewhere
    logger.info("Something went wrong discarding a die; defaulting to Ferocity")
    return False