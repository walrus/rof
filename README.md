# Regiment of Foote

Being a collection of playtest utilities for the _quick_ and _easy_ generation of _odds_ and _outcomes_ for the tabletop game *Regiment of Foote*. 

Uses the Python `logging` module, with the following level meanings:

`logging.DEBUG`   : debug information only
`logging.INFO`    : card draws etc; technical minutiae
`logging.WARNING` : decisions and major events
`logging.ERROR`   : once-a-game events; post-game information and actual errors

Player interaction is handled via `print` statements, rather than the logger