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
    def __init__(self, recipes, fruit_speed):
        self.recipes = recipes
        self.fruit_speed = fruit_speed
        
class BoardUpdatedEvent:
    pass

class FruitSpawnedEvent():
    def __init__(self, fruit):
        self.fruit = fruit

class FruitKilledEvent():
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

class AccelerateFruitsEvent:
    #accelerate the speed of the fruits
    pass
class DecelerateFruitsEvent:
    #accelerate the speed of the fruits
    pass
class FruitSpeedEvent:
    def __init__(self, speed):
        self.speed = speed # in cell/sec

# components subscribed to TickEvent as "input" will be notified first,
# then components with priority as "model", and finally the rest (views). 
PRIO_TICK_INPUT = 1
PRIO_TICK_MODEL = 2

class EventManager:
    
    def __init__(self):
        """ Make 4 sets of callbacks:
        1 for input components(= controllers), they have to be ticked first,
        1 for the model components, ticked just after,
        and 1 for the rendering/view components, ticked at the end.
        Last list = non-tick events.
        """
        self._c_callbacks = set() # controller callbacks for tick event
        self._tc_callbacks = set() # temporary controller callbacks
        
        self._m_callbacks = set() # model
        self._tm_callbacks = set()
        
        self._v_callbacks = set() # view
        self._tv_callbacks = set()
        
        self._callbacks = defaultdict(set) # map non-tick events to their callbacks
        self._tmp_callbacks = defaultdict(set)
        

    def subscribe(self, ev_class, callback, priority=None):
        """ Register a callback for a particular event. """
        if ev_class == TickEvent:
            if priority == PRIO_TICK_INPUT:
                self._tc_callbacks.add(callback)
            elif priority == PRIO_TICK_MODEL:
                self._tm_callbacks.add(callback)
            else: # views/renderers
                self._tv_callbacks.add(callback)
        else:# non-tick events
            self._callbacks[ev_class].add(callback)
        
        
    def publish(self, event):
        """ Publish an event. 
        Tick events go first to controllers, then models, then views.
        """
        ev_class = event.__class__
        if ev_class == TickEvent:
            # iterate over the callbacks: new callbacks will be added to _tc_... 
            for cb in self._c_callbacks:
                cb(event)
            for cb in self._m_callbacks:
                cb(event)
            for cb in self._v_callbacks:
                cb(event)
                
            # iterate over the new callbacks
            while self._tc_callbacks or self._tm_callbacks or self._tv_callbacks:
                # incorporate the new callbacks
                self._c_callbacks = self._c_callbacks.union(self._tc_callbacks)
                self._m_callbacks = self._m_callbacks.union(self._tm_callbacks)
                self._v_callbacks = self._v_callbacks.union(self._tv_callbacks)
                # copy the new callback sets
                c_cbs_cpy = self._tc_callbacks # controller callbacks copy
                m_cbs_cpy = self._tm_callbacks
                v_cbs_cpy = self._tv_callbacks
                # empty the new callback sets
                self._tc_callbacks = set()
                self._tm_callbacks = set()
                self._tv_callbacks = set()
                # iterate over the copies
                for cb in c_cbs_cpy:
                    cb(event)# might add new subscriber callbacks to self._t?_callbacks
                for cb in m_cbs_cpy:
                    cb(event)
                for cb in v_cbs_cpy:
                    cb(event)
                    
        else: # non-tick event
            for cb in self._callbacks[ev_class]:
                cb(event)
            # TODO: non-tick events may have the same problem as tick events
            # So there may need to be the same structure of set-copies.
