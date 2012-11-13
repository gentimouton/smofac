""" 
Model of the game. 
Stores the map name, board, scores, and recipes. 
"""

from board import Board
from config import fruit_speed, map_name, num_recipes_to_win
from constants import RECIPES
from events import RecipeMatchEvent, GameBuiltEvent, MTickEvent, FruitSpeedEvent, \
    AccelerateFruitsEvent, DecelerateFruitsEvent, GameWonEvent


class GameModel:

    def __init__(self, em, ev):
        """Create the board from the map. 
        em is the mode's event manager,
        ev is an event containing data from the previous mode (e.g. menu
        or level transition). ev contains the level number.
        """

        self.score = 0
        self.recipes_made = 0
        self.levelnum = levelnum = ev.levelnum
        if levelnum == 1: # first level
            self.mapname = 'small.txt'
        elif levelnum == 2:
            self.mapname = 'medium.txt'

        # build the recipe tree = dict of dict of ... of dict, 
        # depth = length of the longest recipe 
        self.recipes = {}
        longest_recipe_length = 0 # length of the longest recipe
        lowest_recipe_score = 0 # arbitrary value to start with
        # it can be that some recipes have a negative value!

        for recipe, score in RECIPES.items():
            longest_recipe_length = max(longest_recipe_length, len(recipe))
            lowest_recipe_score = min(lowest_recipe_score, score)

            # build the tree-path for that recipe 
            bucket = self.recipes
            for fruit in recipe:
                if fruit not in bucket:
                    bucket[fruit] = {}
                bucket = bucket[fruit]
            bucket['score'] = score # no fruit should be named 'score'!

        self.lowest_recipe_score = lowest_recipe_score

        # create the board
        self.board = Board(self, em, self.mapname, longest_recipe_length)

        self.fruit_speed = fruit_speed # in cells per second
        # 1 tick for anticipating and setting movement direction, 
        # and another for actually moving fruits
        self.base_fruit_timer = 1000. / self.fruit_speed / 2
        self.fruit_mvt_timer = self.base_fruit_timer # decreased each clock tick
        self.fruit_mvt_phase = False # whether currently in movement phase 

        self._em = em
        em.subscribe(MTickEvent, self.on_tick)
        em.subscribe(AccelerateFruitsEvent, self.on_faster_fruits)
        em.subscribe(DecelerateFruitsEvent, self.on_slower_fruits)

        # RECIPES = dict: tuples of fruit type -> score
        em.publish(GameBuiltEvent(RECIPES, self.fruit_speed))


    def recipe_match(self, fruit_list):
        """ Return whether fruits in the waiting cells should wait some more.
        If fruits dont need to wait, return the number of fruits to kill.
        If number of fruits to kill is 0, then all fruits should keep looping. 
        Some of the fruits in the list may be None;
        it means that spot has no fruit.
        """
        bucket = self.recipes
        # store the matching recipe with highest score
        best_recipe_score = (None, self.lowest_recipe_score - 1)
        saw_mismatch = False # whether a prefix of the fruit list does NOT match any recipe prefix

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
            max_suffix_score = self.__highest_bucket_recipe(bucket)
            is_prefix_of_better_recipe = max_suffix_score > score
            if not saw_mismatch and is_prefix_of_better_recipe:
                # beginning of a longer recipe: wait for more fruits
                return True, -1
            else: # either saw a mismatch, or the recipe takes all possible slots
                # update the score, and process the fruits
                self.score += score
                self.recipes_made += 1
                if self.recipes_made >= num_recipes_to_win:
                    ev = GameWonEvent(self.levelnum, self.score)
                else:
                    ev = RecipeMatchEvent(recipe, self.score, score)
                self._em.publish(ev)
                # tell the board how many fruits to kill
                return False, len(recipe)

        else: # no entire recipe matches
            if not saw_mismatch: # only the beginning of a recipe was found
                return True, -1
            else: # no match and not even the beginning of a match: keep moving 
                return False, 0


    def __highest_bucket_recipe(self, bucket):
        """ Return (recipe, score) of the recipe with highest score
        in the bucket """
        node_score = [bucket['score']]
        children_scores = [self.__highest_bucket_recipe(bucket[child])
                           for child in bucket if child != 'score']
        return max(node_score + children_scores)


    def on_tick(self, tickevt):
        """ If it's time, ask the board to move the fruits. """

        elapsed_millis = tickevt.loopduration
        self.fruit_mvt_timer -= elapsed_millis
        if self.fruit_mvt_timer <= 0:
            if self.fruit_mvt_phase: # movement
                self.board.progress_fruits()
            else:
                self.board.predict_fruits()
            self.fruit_mvt_timer = self.base_fruit_timer
            self.fruit_mvt_phase = not self.fruit_mvt_phase



    def on_faster_fruits(self, ev):
        """ Increase the speed of the fruits """
        self.fruit_speed += .2 # by 0.2 cell per sec
        self.base_fruit_timer = 1000. / self.fruit_speed / 2
        ev = FruitSpeedEvent(self.fruit_speed)
        self._em.publish(ev)

    def on_slower_fruits(self, ev):
        """ Decrease the speed of fruits """
        self.fruit_speed -= .2
        self.base_fruit_timer = 1000. / self.fruit_speed / 2
        ev = FruitSpeedEvent(self.fruit_speed)
        self._em.publish(ev)
