from collections import defaultdict, deque

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
class BoardPredictedEvent:
    pass

class FruitSpawnedEvent():
    def __init__(self, fruit):
        self.fruit = fruit
class FruitPlacedEvent():
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
class CTickEvent(TickEvent): # controllers tick
    pass
class MTickEvent(TickEvent): # models tick
    pass
class VTickEvent(TickEvent): # views tick
    pass


class QuitEvent(): 
    # player wants to exit the game
    pass

class TriggerTrapEvent(): 
    # player pushed the trap key
    pass


class ValidateEvent():
    # player pushed Enter
    pass

# Should these 4 events be merged in a single ArrowKeyEvent?
class MoveUpEvent():
    pass
class MoveDownEvent():
    pass
class MoveLeftEvent():
    pass
class MoveRightEvent():
    pass


class FruitSpeedEvent:
    def __init__(self, speed):
        self.speed = speed#change the speed of fruits
class AccelerateFruitsEvent:
    pass#Increase the speed of the fruits
class DecelerateFruitsEvent:
    pass#decrease the speed of the fruits




class EventManager:
    
    def __init__(self):
        # map events to their callbacks
        self._callbacks = defaultdict(set)
        # store the callbacks added during this frame
        self._new_callbacks = defaultdict(set) 
        self.eventdq = deque()

    def subscribe(self, ev_class, callback):
        """ Register a callback for a particular event. """
        self._new_callbacks[ev_class].add(callback)
        


    def join_new_listeners(self):
        """ add new listener callbacks to the current callbacks """
        if self._new_callbacks:
            for evClass in self._new_callbacks:
                self._callbacks[evClass] = self._callbacks[evClass].union(self._new_callbacks[evClass])
            self._new_callbacks.clear() 

   
    def publish(self, event):
        """ Publish an event.
        New subscriber callbacks are added when tick events are processed.    
        """        
        
        if event.__class__ in [CTickEvent, MTickEvent, VTickEvent]:
            self.join_new_listeners() #necessary for at least the very first tick
            while self.eventdq:
                ev = self.eventdq.popleft()
                
                self.join_new_listeners()
                for callback in self._callbacks[ev.__class__]: 
                    # Some of these listeners may enqueue events on the fly.
                    # Those new events will be treated within this while loop,
                    # they don't have to wait for the next tick event.
                    callback(ev)
                
                self.join_new_listeners()
                
            # finally, post tick event
            for cb in self._callbacks[event.__class__]:
                cb(event)
                
            self.join_new_listeners()
            
            
        else: # non-tick event
            self.eventdq.append(event)
            
