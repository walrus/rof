""" Constants to fiddle with """
from enum import Enum

# If you have more than N cards, take the best N
# Means that more cards is good but preserves E.G distance dynamics for shooting
BEST_OF_SHOOTING = 3
BEST_OF_FIGHTING = 4

# How many Disorder you need to accumulate in one action to Panic
# 3 is nice because then it's possible, albeit unlikely, in normal shooting
PANIC_THRESHOLD = 3

# Threshold at which you will need to panic test for every single Disorder gained
# Trialling this at 21 (at which point you can only pass on two Kings anyway)
AUTO_PANIC_THRESHOLD = 21

# What's a good default steadiness? Jack?
DEFAULT_STEADINESS = 10

# Ranges are determined by the max sum of 3 cards (30); cannon double this and pistols halve it
PISTOL_RANGE = 15
MUSKET_RANGE = 30
CANNON_RANGE = 60

# Charge ranges are max of two cards (unblown Cavalry) or one card (everyone else)
TWO_CARD_CHARGE_MAX = 20
SINGLE_CARD_CHARGE_MAX = 10

# Minimum distance for the purposes of calculating shooting casualties 
MIN_SHOOTING_DISTANCE = 8

# Similar effect; minimum threshold for calculating fighting casualties
MIN_FIGHTING_THRESHOLD = 8

class Faction(Enum):
    Royalist = 0
    Parliamentarian = 1
    # Maybe I'll add the Scots later...
