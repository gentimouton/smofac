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
        self.recipes = RECIPES
        self.mapname = MAPNAME 
        
        self.board = Board(self, em, self.mapname)
        
        self._em = em
        
        
    def recipe_match(self, fruit_list):
        """ When a recipe matches, increase the score """
        if fruit_list in self.recipes.keys():
            recipe_score = self.recipes[fruit_list]
            self.score += recipe_score
            ev = RecipeMatchEvent(self.score, recipe_score)
            self._em.publish(ev)
            return True
        else:
            return False
