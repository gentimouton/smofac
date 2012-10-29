
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


