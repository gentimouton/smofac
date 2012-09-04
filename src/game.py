""" 
Model: map name, board, scores, and recipes.
View: score and recipe widgets on the right, board on the left.
"""
from board import Board
from constants import MAPNAME, RECIPES
from events import RecipeMatchEvent
import logging



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
        
        self.max_recipe_length = max_recipe_length
        
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
        TODO: this does not make 3-in-a-row wait for 4-in-a-row 
        """
        bucket = self.recipes
        best_recipe_score = (None, -1) # store the matching recipe with highest score
        # TODO: -1 means that recipes with scores below 0 won't be able to leave!
        saw_mismatch = False
        
        for i, fruit in enumerate(fruit_list):
            if not fruit: # a hole means that so far, 
                # the fruits were matching the beginning of a recipe
                break # saw_mismatch is still False 
            if fruit.fruit_type in bucket:
                bucket = bucket[fruit.fruit_type] # keep going down the tree
                if 'score' in bucket and bucket['score'] > best_recipe_score[1]:
                    # only keep the best recipe
                    recipe = fruit_list[:i + 1]
                    score = bucket['score']
                    best_recipe_score = (recipe, score)
                # saw_mismatch still False
            else: # mismatch: stop going down the tree
                saw_mismatch = True
                break
        
        recipe, score = best_recipe_score
        if recipe: # a recipe matches
            if not saw_mismatch and self._is_prefix_of_better_recipe(recipe): 
                # beginning of a longer recipe: wait for more fruits
                return -1
            else: # either saw a mismatch, or the recipe takes all possible slots
                # update the score, and process the fruits
                self.score += score
                ev = RecipeMatchEvent(self.score, score) # TODO: also add the recipe
                self._em.publish(ev)
                # tell the board how many fruits to kill
                return len(recipe)
                    
        else: # no entire recipe matches
            if not saw_mismatch: # only the beginning of a recipe was found
                return -1
            else: # no match and not even the beginning of a match: keep moving 
                return 0


    def _is_prefix_of_better_recipe(self, recipe):
        """ return True if list of fruits is a strict prefix of a recipe
        worth more points. """

        bucket = self.recipes
        # find the recipe's bucket
        for fruit in recipe:
            if fruit.fruit_type in bucket:
                bucket = bucket[fruit.fruit_type] # keep going down the tree
            else:
                logging.error('Recipe should have matched a bucket')
                return False # process the fruits anyway

        # if another recipe in the bucket, it means prefix
        if 'score' not in bucket:
            logging.error('\'score\' should have been in bucket.')
            return False # process that mess if possible...
                    
        return len(bucket) > 1 # 1 because 'score' is one of the leaves
