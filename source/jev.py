""" Calls Jev to make simulated player decisions """
from source.cards import Card

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

def chooseActivationCard(cards : list[Card]) -> Card:
    """ Ask Jev to choose a card from hand to use for activation"""
    # We don't need the value part of the dict for this query, but Jev requires it as a dict
    cardDict = {str(card): None for card in cards}
    with TypeSafeClient() as client:
        response = client.system_one(
            state={"document": "I'm playing a game. As part of this game I need to pick a card from the given hand. Higher cards are better, but if I have cards from the same suit I want to save them for other things."},
            questions={
                "card": Choice(
                    instructions="Which card should I choose?",
                    criteria=cardDict,
                ),
            },
        )
        cardChoice = response.answers["card"]
        if cardChoice:
            print(f"Jev chose: {cardChoice}")
            card = Card.fromShortString(cardChoice)
            if card:
                return card
            # Otherwise it failed to parse for some reason

    # Fallback if I've messed up somewhere
    print(f"Something went wrong; defaulting to {cards[0]}")
    return cards[0]