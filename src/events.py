from collections import defaultdict

class Event:
    def __repr__(self):
        return str(self.__class__)
    def __str__(self):
        return self.__repr__()

class BoardBuiltEvent(Event):
    def __init__(self, width, height, board):
        self.width = width
        self.height = height
        self.board = board

class GameBuiltEvent():
    def __init__(self, recipes):
        self.recipes = recipes
        
class BoardUpdatedEvent:
    def __init__(self, fruits):
        self.fruits = fruits
    
class FruitSpawnedEvent():
    def __init__(self, fruit):
        self.fruit = fruit
      
class RecipeMatchEvent():
    def __init__(self, recipe, current_score, recipe_score):
        self.recipe = recipe
        self.current_score = current_score
        self.recipe_score = recipe_score

class TickEvent:
    def __init__(self, loopmillis, workmillis):
        self.loopduration = loopmillis # how long since last tick
        self.workduration = workmillis

class QuitEvent(): 
    # player wants to exit the game
    pass

class TriggerTrapEvent(): 
    # player pushed the trap key
    pass


# components subscribed to TickEvent as "input" will be notified first,
# then components with priority as "model", and finally the rest (views). 
PRIO_TICK_INPUT = 1
PRIO_TICK_MODEL = 2


class EventManager:
    """ This object coordinates the communication between components.
    See http://stackoverflow.com/questions/7249388/python-duck-typing-for-mvc-event-handling-in-pygame
    """

    def __init__(self):
        """ Make 4 lists of callbacks:
        1 for input components(= controllers), they have to be ticked first,
        1 for the model components, ticked just after,
        and 1 for the rendering/view components, ticked at the end.
        Last list = non-tick events.
        """
        self._ctrlers_callbacks = defaultdict(list)
        self._models_callbacks = defaultdict(list)
        self._views_callbacks = defaultdict(list)
        self._callbacks = defaultdict(list)

        
    def subscribe(self, ev_class, callback, priority=None):
        """ Register a callback for a particular event. """
        if ev_class == TickEvent:
            if priority == PRIO_TICK_INPUT:
                self._ctrlers_callbacks[ev_class].append(callback)
            elif priority == PRIO_TICK_MODEL:
                self._models_callbacks[ev_class].append(callback)
            else: # views/renderers
                self._views_callbacks[ev_class].append(callback)
        else:# non-tick events
            self._callbacks[ev_class].append(callback)
        
    def publish(self, event):
        """ Publish an event. """
        ev_class = event.__class__
        if ev_class == TickEvent:
            for cb in self._ctrlers_callbacks[ev_class]:
                cb(event)
            for cb in self._models_callbacks[ev_class]:
                cb(event)
            for cb in self._views_callbacks[ev_class]:
                cb(event)
        else: # non-tick event
            for cb in self._callbacks[ev_class]:
                cb(event)
