
# TODO: make a config file

# mechanics config
SPAWNFREQ = 3 # spawn 1 fruit every how many cells?
FRUIT_SPEED = 2 # in cells per second
RNGSEED = 2
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
RECIPES = {('S', 'S', 'S'): 10,
           ('S', 'S', 'S', 'S'): 40,
           ('K', 'K', 'K'): 10,
           ('K', 'K', 'K', 'K'): 40,
           ('B', 'B', 'B'): 10,
           ('B', 'B', 'B', 'B'): 40,
           ('J', 'J', 'J'): 10,
           ('J', 'J', 'J', 'J'): 40,
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
FPS = 60
BG_COLOR = (111, 111, 111)
TRAP_COLOR = (11, 11, 11)
PATH_COLOR = (233, 233, 233)
BLENDER_COLOR = (155, 155, 155)

# maps are 12x12: 600x600px on the left for the board, 
# 200x600px on the right for the UI
RESOLUTION = (800, 600)
CELLSIZE = 50

FONT_SIZE = 30 # in px
