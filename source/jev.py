""" Calls Jev to make simulated player decisions """
from typesafe_sdk import Choice, TypeSafeClient

from source.cards import Card


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
            card = Card.fromShortString(cardChoice.choice)
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
            card = Card.fromShortString(cardChoice.choice)
            if card:
                return card
            # Otherwise it failed to parse for some reason; fall back to the first card in the list
    
    # Fallback if I've messed up somewhere
    print(f"Something went wrong discarding; defaulting to {cards[0]}")
    return cards[0]