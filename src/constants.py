
# TODO: make a config file

# mechanics config
SPAWNFREQ = 5
RNGSEED = 0
MAPNAME = 'medium.txt'

# map constants
DIR_UP = 'U'
DIR_DOWN = 'D'
DIR_LEFT = 'L'
DIR_RIGHT = 'R'
DIR_MAP = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]

# fruits 
# TODO: replace with constants rather than string slugs?
# NO FRUIT CAN BE NAMED 'score'!
FRUIT_LIST = ['strawb', 'kiwi', 'blueb', 'banana'] 
# TODO: should be able to specify X,X,X for triple-whatever as a recipe
RECIPES = {#('strawb', 'strawb', 'strawb'):10,
           ('strawb', 'strawb', 'strawb', 'strawb'):30,
           #('kiwi', 'kiwi', 'kiwi'):10,
           ('kiwi', 'kiwi', 'kiwi', 'kiwi'):30,
           #('blueb', 'blueb', 'blueb'):10,
           ('blueb', 'blueb', 'blueb', 'blueb'):30,
           #('banana', 'banana', 'banana'): 10,
           ('banana', 'banana', 'banana', 'banana'): 30,
           }

# graphics config
FRUIT_COLORS = {'strawb': (222, 55, 55),
               'kiwi': (55, 222, 55),
               'blueb': (55, 55, 222),
               'banana': (222, 222, 22)
               }
FPS = 3
BOARD_BGCOLOR = (33, 33, 33)
CELLSIZE = 50
RESOLUTION = (800, 600)
FONT_SIZE = 30 # in px
