""" 
Model: map name, board, scores, and recipes.
View: score and recipe widgets on the right, board on the left.
"""
from board import Board
from constants import MAPNAME, RECIPES
from events import RecipeMatchEvent



class Game:
    
    def __init__(self, em):
        """Create the board from the map. """
        
        self.score = 0
        self.mapname = MAPNAME 
        
        
        # build the recipe tree = dict of dict of ... of dict, 
        # depth = length of the longest recipe 
        self.recipes = {}
        max_recipe_length = 0 # length of the longest recipe
        for recipe, score in RECIPES.items():
            max_recipe_length = max(max_recipe_length, len(recipe))
            
            # build the tree-path for that recipe 
            bucket = self.recipes
            for fruit in recipe:
                if fruit not in bucket:
                    bucket[fruit] = {}
                bucket = bucket[fruit]
            bucket['score'] = score # no fruit should be named 'score'!
        
        # create the board
        self.board = Board(self, em, self.mapname, max_recipe_length)
        
        self._em = em
        
        
    def recipe_match(self, fruit_list):
        """ When fruits match one or more recipes, 
        return the number of fruits that match the recipe with highest score, 
        and increase the score.
        When fruits match the beginning of a recipe, we need to wait for more,
        and return -1 for "wait for more".
        When fruits don't match any recipe or beginning of recipe,
        return 0.
        Some of the fruits in the list may be None: that spot has no fruit.
        """
        bucket = self.recipes
        matching_recipes = [] # store all recipes that match, with their score
        wait_for_more = True
        for i, fruit in enumerate(fruit_list):
            if not fruit: # a hole: so far, the fruits were matching the beginning of a recipe
                break # wait_for_more remains True 
            if fruit.fruit_type in bucket:
                bucket = bucket[fruit.fruit_type] # keep going down the tree
                if 'score' in bucket:
                    recipe = fruit_list[:i + 1]
                    score = bucket['score']
                    matching_recipes.append((recipe, score))
            else: # mismatch: stop going down the tree
                wait_for_more = False # no need to wait for more
                break
        
        if matching_recipes: # at least one recipe matches
            # find matching recipe with highest score
            recipe, recipe_score = max(matching_recipes, key=lambda pair: pair[1])
            # update score
            self.score += recipe_score
            ev = RecipeMatchEvent(self.score, recipe_score)
            self._em.publish(ev)
            # tell the board how many fruits to kill
            return len(recipe)
        
        elif wait_for_more: # only the beginning of a recipe was found
            return -1
            
        else: # no match and not even the beginning of a match 
            return 0
