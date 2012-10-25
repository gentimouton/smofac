from collections import defaultdict, deque

class Event:
    def __repr__(self):
        return self.__class__.__name__
    def __str__(self):
        return self.__repr__()
    

class BoardBuiltEvent(Event):
    def __init__(self, width, height, board):
        self.width = width
        self.height = height
        self.board = board

class GameBuiltEvent(Event):
    def __init__(self, recipes, fruit_speed):
        self.recipes = recipes
        self.fruit_speed = fruit_speed
        
class BoardUpdatedEvent(Event):
    pass
class BoardPredictedEvent(Event):
    pass

class FruitSpawnedEvent(Event):
    def __init__(self, fruit):
        self.fruit = fruit
class FruitPlacedEvent(Event):
    def __init__(self, fruit):
        self.fruit = fruit
        
class FruitKilledEvent(Event):
    def __init__(self, fruit):
        self.fruit = fruit
              
class RecipeMatchEvent(Event):
    def __init__(self, recipe, current_score, recipe_score):
        self.recipe = recipe
        self.current_score = current_score
        self.recipe_score = recipe_score


class TickEvent(Event):
    def __init__(self, loopmillis, workmillis):
        self.loopduration = loopmillis # how long since last tick
        self.workduration = workmillis
class CTickEvent(TickEvent): # controllers tick
    pass
class MTickEvent(TickEvent): # models tick
    pass
class VTickEvent(TickEvent): # views tick
    pass


class QuitEvent(Event):
    pass # player wants to exit the game


class TriggerTrapEvent(Event): 
    pass # player pushed the trap key


class ValidateEvent(Event):
    pass # player pushed Enter


class MoveUpEvent(Event):
    pass
class MoveDownEvent(Event):
    pass
class MoveLeftEvent(Event):
    pass
class MoveRightEvent(Event):
    pass


class FruitSpeedEvent(Event):
    def __init__(self, speed):
        self.speed = speed#change the speed of fruits
class AccelerateFruitsEvent(Event):
    pass#Increase the speed of the fruits
class DecelerateFruitsEvent(Event):
    pass#decrease the speed of the fruits



# mode switching events
class ToGameEvent(Event):
    pass
class ToMenuEvent(Event):
    pass


class EventManager:
    
    def __init__(self):
        # map events to their callbacks
        self._callbacks = defaultdict(set)
        # store the callbacks added during this frame
        self._new_callbacks = defaultdict(set)
        # store the callbacks to be removed this frame
        self._dead_callbacks = defaultdict(set)
        self.eventdq = deque()


    def subscribe(self, ev_class, callback):
        """ Register a callback for a particular event. """
        self._new_callbacks[ev_class].add(callback)

    def unsubscribe(self, ev_class, callback):
        """ Unregister a callback for an event """
        self._dead_callbacks[ev_class].add(callback)
        

    def update_listeners(self):
        """ Add new listener callbacks to the current callbacks,
        and remove dead callbacks from the current callbacks.
        """
        if self._dead_callbacks:
            for evClass in self._dead_callbacks:
                self._callbacks[evClass] -= self._dead_callbacks[evClass]
            self._dead_callbacks.clear()
            
        if self._new_callbacks:
            for evClass in self._new_callbacks:
                self._callbacks[evClass] |= self._new_callbacks[evClass]
            self._new_callbacks.clear()
        
    def clear(self):
        """ Remove all listeners. """
        self._callbacks.clear()
        self._dead_callbacks.clear()
        self._new_callbacks.clear()
        self.eventdq.clear()
         
   
    def publish(self, event):
        """ Publish an event.
        New subscriber callbacks are added when tick events are processed.    
        """        
        
        if event.__class__ in [CTickEvent, MTickEvent, VTickEvent]:
            self.update_listeners() #necessary for at least the very first tick
            while self.eventdq:
                ev = self.eventdq.popleft()
                
                #self.update_listeners() # TODO: remove
                for callback in self._callbacks[ev.__class__]: 
                    # Some of these listeners may enqueue events on the fly.
                    # Those new events will be treated within this while loop,
                    # they don't have to wait for the next tick event.
                    callback(ev)
                
                self.update_listeners()
                
            # finally, post tick event
            for cb in self._callbacks[event.__class__]:
                cb(event)
                
            self.update_listeners()
            
            
        else: # non-tick event
            self.eventdq.append(event)
            
