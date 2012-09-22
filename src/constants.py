
# TODO: make a config file

# mechanics config
SPAWN_PERIOD = 1 # spawn a fruit every how many seconds?
FRUIT_SPEED = 4 # in cells per second
# thus there is a fruit spawned every SPAWN_PERIOD * FRUIT_SPEED cells
# careful: if FRUIT_SPEED < 1/SPAWN_PERIOD, the 2nd fruit causes game over 


RNGSEED = 1
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

doubles = {('S', 'S'): 4,
           ('K', 'K'): 4,
           ('B', 'B'): 4,
           ('J', 'J'): 4,
           }

triples = {('S', 'S', 'S'): 10,
           ('K', 'K', 'K'): 10,
           ('B', 'B', 'B'): 10,
           ('J', 'J', 'J'): 10,
           }

quads = {('S', 'S', 'S', 'S'): 40,
         ('K', 'K', 'K', 'K'): 40,
         ('B', 'B', 'B', 'B'): 40,
         ('J', 'J', 'J', 'J'): 40,
         }

xyx = {('S', 'K', 'S'):10,
       ('S', 'B', 'S'):10,
       ('B', 'K', 'B'):10,
       ('B', 'S', 'B'):10,
       ('K', 'B', 'K'):10,
       ('K', 'S', 'K'):10,
       }

RECIPES = {}
#RECIPES.update(doubles)
RECIPES.update(triples)
RECIPES.update(quads)


# graphics config
FRUIT_COLORS = {'S': (222, 55, 55),
               'K': (55, 222, 55),
               'B': (55, 55, 222),
               'J': (222, 222, 55)
               }

BG_COLOR = (111, 111, 111)
TRAP_COLOR = (11, 11, 11)
PATH_COLOR = (233, 233, 233)
BLENDER_COLOR = (155, 155, 155)


# frame rate, per second
FPS = 30

# How many positions a fruit can take in one cell.
# If even number, the first interpolation step will be right between 2 cells.
# The user may not know which cell the fruit belongs to. 
# Thus, pick odd numbers.
# Also, it should ideally be a divider of FPS to avoid jittery movement. 
STEPS_PER_CELL = 5

# Width and height of cells, in px.
# Should be a multiple of STEPS_PER_CELL, otherwise there may be 
# a slight jittery movement due to float rounding
CELLSIZE = 50

# Width and height of the screen in px. Better if multiple of CELLSIZE,
# otherwise there is a stripe left over at bottom and/or right of the screen.
RESOLUTION = (800, 600)
# Like this, map is 12x12: 600x600px on the left for the board, 
# 200x600px on the right for the UI

FONT_SIZE = 30 # in px
