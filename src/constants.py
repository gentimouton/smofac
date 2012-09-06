
# TODO: make a config file

# mechanics config
SPAWNFREQ = 4
RNGSEED = 0
MAPNAME = 'medium.txt'
RECIPES_MADE_WIN_CONDITION = 8 # how many recipes to make to win 

# map constants
DIR_UP = 'U'
DIR_DOWN = 'D'
DIR_LEFT = 'L'
DIR_RIGHT = 'R'
DIR_MAP = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]

# fruits 
# TODO: replace with constants rather than string slugs?
# NO FRUIT CAN BE NAMED 'score'!
FRUIT_LIST = ['S', 'K', 'B', 'J'] 
# TODO: should be able to specify X,X,X for triple-whatever as a recipe

# triples only
#RECIPES = {('S', 'S', 'S'):10,
#           ('K', 'K', 'K'):10,
#           ('B', 'B', 'B'):10,
#           ('J', 'J', 'J'): 10,
#           }

# triples + quadruples
RECIPES = {('S', 'S', 'S'):10,
           ('S', 'S', 'S', 'S'):30,
           ('K', 'K', 'K'):10,
           ('K', 'K', 'K', 'K'):30,
           ('B', 'B', 'B'):10,
           ('B', 'B', 'B', 'B'):30,
           ('J', 'J', 'J'): 10,
           ('J', 'J', 'J', 'J'): 30,
           }

# XYX
#RECIPES = {('S', 'K', 'S'):10,
#           ('S', 'B', 'S'):10,
#           ('B', 'K', 'B'):10,
#           ('B', 'S', 'B'):10,
#           ('K', 'B', 'K'):10,
#           ('K', 'S', 'K'):10,
#           }


# graphics config
FRUIT_COLORS = {'S': (222, 55, 55),
               'K': (55, 222, 55),
               'B': (55, 55, 222),
               'J': (222, 222, 22)
               }
FPS = 2
BOARD_BGCOLOR = (33, 33, 33)
CELLSIZE = 50
RESOLUTION = (800, 600)
FONT_SIZE = 30 # in px
