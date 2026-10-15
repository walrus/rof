"""Represents the actual people playing the game"""

import logging
from typing import Any

from source.cards import Card, combinations, draw, highestCombination, sumCards
from source.commission import Colonel
from source.constants import Faction
from source.jev import (
    chooseActivationCard,
    chooseCardToDiscard,
    chooseCommand,
    chooseDieToLose,
)
from source.units import Command, Unit, basicCommands

logger = logging.getLogger(__name__)

#TODO: proper abstract class etc
class Player:
    name: str
    faction: Faction
    unit: Unit
    colonel: Colonel
    hand: list[Card]

    def __init__(self, name, faction, colonel, unit):
        self.name = name
        self.faction = faction
        self.colonel = colonel
        self.unit = unit
        self.hand = draw(colonel.grip, colonel.grip)

        # Monkey patch some functions on Unit so that they can refer back to the Player for decisions
        unit.chooseDieToLose = self.chooseDieToDiscard

    @property
    def grip(self):
        return self.colonel.grip

    def drawStep(self) -> None:
        self.hand.extend(draw(2,2))

    def enforceHandSize(self) -> None:
        if len(self.hand) <= self.grip:
            return

        # Otherwise got to get rid of some - most of the time this will be only one
        # but it's possible to E.G lose more than one Grip in a turn
        while len(self.hand) > self.grip:
            cardChoice = chooseCardToDiscard(self.hand)
            logger.info(f"{self.name} chooses to discard a {cardChoice!s}")
            self.hand.remove(cardChoice)

    def commandOptions(self, enemies: list[Unit]) -> dict[str, Command | None]:
        """ Get all possible Commands, ruling out any that no combination of cards in hand can play"""
        highestCardCombo = highestCombination(self.hand)
        return {command.name: command for command in basicCommands if command.isPossible(highestCardCombo, self.unit, enemies)}

    # Abstract methods for making decisions implemented by subclasses

    def chooseActivationCard(self) -> Card:
        return self.hand[0] # Hand guaranteed to contain at least two cards at this point

    def chooseCommand(self, enemies: list[Unit]) -> Command | None:
        return None
    
    def chooseDieToDiscard(self) -> bool:
            # True for Firepower; false for ferocity
            return False

class HumanPlayer(Player):
    # Passes information to the terminal and waits for input to make decisions
    # TODO default that is accepted if you just hit enter
    def _selectFromOptions(self, options: dict[str, Any], default: str) -> str:
        # print a list of options and return the index a player selects
        # Enforces a selection from within the list
        for key, option in options.items():
            print(f"{key}: {option!s}")
        print(f"Default (Enter): {default}")

        tries = 0
        while tries < 10:
            choice = input()
            if not choice: # Enter pressed!
                return default
            if choice in options:
                return choice
            else:
                print(f"Choice {choice} is not a valid options try again")

            tries = tries + 1
        return default
    
    def chooseActivationCard(self) -> Card:
        print(f"\n{self.name}, pick a card to activate with: ")
        handOptions = {str(i): self.hand[i] for i in range(len(self.hand))}
        cardChoice = handOptions[self._selectFromOptions(handOptions, str(len(handOptions)-1))] # TODO default select lowest card not last
        self.hand.remove(cardChoice)
        return cardChoice

    def chooseCommand(self, enemies: list[Unit]) -> Command | None:
        # Choose a command, then the combination of cards to play it with
        options : dict[str, Command | None ] = self.commandOptions(enemies)
        
        if not options:
            logger.info("No options available!")
            return None

        print(f"\n{self.name}, choose a command to play (your available hand is {' '.join(str(card) for card in self.hand)})")
        options['Nothing'] = None
        #TODO: pretty ew as well
        optionStrings = {key: option.description if option else "Let the unit continue as is" for key, option in options.items()}
        chosenCommand = options[self._selectFromOptions(optionStrings, 'Nothing')]

        if not chosenCommand:
            print("Doing nothing; no cards need be played")
            return None

        cardCombos = combinations(self.hand)
        requiredDifficulty = chosenCommand.currentDifficulty(self.unit)

        usefulCombos = [combo for combo in cardCombos if combo[0] >= requiredDifficulty]
        comboOptions = {str(i): f"{' '.join(str(card) for card in combo[1])} ({combo[0]} total)" for i, combo in enumerate(usefulCombos)}
        print(f"Choose some cards to play your Command with (required difficulty {requiredDifficulty})")
        comboChoice = self._selectFromOptions(comboOptions, str(len(comboOptions) - 1))

        #TODO: ew
        chosenCards = usefulCombos[int(comboChoice)][1]
        for card in chosenCards:
            self.hand.remove(card)

        # Fill out details of the Command now we know the cards used
        # TODO: work on target choice; for now always pick the sole enemy
        if chosenCommand.name in ['Fire', 'Charge']:
            chosenCommand.target = enemies[0]
        elif chosenCommand.name in ['Walk', 'Run', 'Trot', 'Gallop']:
            chosenCommand.direction = self.unit.directionOf(enemies[0])
        elif chosenCommand.name in ['Flee']:
            directionTo = self.unit.directionOf(enemies[0])
            chosenCommand.direction = (directionTo[0] * -1, directionTo[1] * -1)
        elif chosenCommand.name in ['Encourage']:
            chosenCommand.cardsUsed = chosenCards

        return chosenCommand

    def chooseDieToDiscard(self) -> bool:
        print(f"\n{self.name}, pick a die to discard. ")
        print(f"{self.unit.name()} currently has {self.unit.firepower} Firepower and {self.unit.ferocity} Ferocity")

        dieOptions = {
            '0': 'Firepower',
            '1': 'Ferocity'
        }
        dieChoice = self._selectFromOptions(dieOptions, 'Ferocity')

        return dieChoice == '0'

class AIPlayer(Player):
    # Uses Jev to make decisions instead of asking about them
    
    def chooseActivationCard(self) -> Card:
        """ Pick and spend an activation card, using Jev to choose """
        cardChoice = chooseActivationCard(self.hand)
        self.hand.remove(cardChoice)
        return cardChoice

    def chooseCommand(self, enemies: list[Unit]) -> Command | None:
            """ Pick a command to give """
            options = self.commandOptions(enemies)
    
            if not options:
                logger.info("No Command options available!")
                return None
    
            cardCombos = combinations(self.hand)
    
            chosenCommand, chosenCards = chooseCommand(self.unit, enemies, options, cardCombos)
    
            logger.warning(f"Playing command {chosenCommand.name if chosenCommand else 'None'} with {' '.join(str(card) for card in chosenCards) if chosenCards else 'no cards'}")
    
            if not chosenCommand:
                return None
    
            diff = chosenCommand.currentDifficulty(self.unit)
            chosenSum = sumCards(chosenCards)
            if chosenSum < diff:
                # Blunder! TODO: write the Blunder table
                logger.warning(f"{self.name} has Blundered, trying play {chosenCommand.name} (Difficulty {diff}) with cards totalling {chosenSum}!")
                return None
            
            for card in chosenCards:
                self.hand.remove(card)
    
            # TODO: work on target choice; for now always pick the sole enemy
            if chosenCommand.name in ['Fire', 'Charge']:
                chosenCommand.target = enemies[0]
            elif chosenCommand.name in ['Walk', 'Run', 'Trot', 'Gallop']:
                chosenCommand.direction = self.unit.directionOf(enemies[0])
            elif chosenCommand.name in ['Flee']:
                directionTo = self.unit.directionOf(enemies[0])
                chosenCommand.direction = (directionTo[0] * -1, directionTo[1] * -1)
            elif chosenCommand.name in ['Encourage']:
                chosenCommand.cardsUsed = chosenCards
            return chosenCommand

    def chooseDieToDiscard(self) -> bool:
        # True for Firepower; false for ferocity
        return chooseDieToLose(self.unit)