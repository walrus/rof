""" Constants to fiddle with """

# If you have more than N cards, take the best N
# Means that more cards is good but preserves E.G distance dynamics for shooting
BEST_OF = 3

# How many Disorder you need to accumulate in one action to Panic
# 3 is nice because then it's possible, albeit unlikely, in normal shooting
PANIC_THRESHOLD = 3

# What's a good default steadiness? Jack?
DEFAULT_STEADINESS = 10