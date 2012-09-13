from constants import SPAWN_PERIOD, RNGSEED, FRUIT_LIST
from events import FruitSpawnedEvent, TickEvent
from fruit import Fruit
import logging
import random

class Spawner():
    def __init__(self, em, cell):
        self.rng = random.Random()
        self.rng.seed(RNGSEED) # determinism = easier to debug
        self.spawn_timer = 0 # start spawning right away 
        self.fruits_spawned = 0 # ++ when a fruit appears
        self.cell = cell 
        self._em = em
        em.subscribe(TickEvent, self.on_tick)
        
        
    def on_tick(self, ev):
        """ Spawn a fruit if it's time to do it. 
        Return (a, b), where a is whether it had to spawn,
        and b the fruit (if succeeded).
        This is called by the board every model tick.
        """
        
        duration = ev.loopduration
        self.spawn_timer -= duration
        if self.spawn_timer <= 0:
            if self.cell.fruit: # should spawn new fruit, but can't: game over!
                logging.info('game over') # TODO: QuitEvent
            else: # can spawn: game keeps going
                random_int = self.rng.randint(0, len(FRUIT_LIST) - 1)
                fruit_type = FRUIT_LIST[random_int]
                fruit = Fruit(self.cell, fruit_type, self.fruits_spawned)
                self.cell.fruit = fruit
                self.spawn_timer = SPAWN_PERIOD * 1000
                self.fruits_spawned += 1
                logging.debug('spawned Fruit %s' % fruit)
                ev = FruitSpawnedEvent(fruit)
                self._em.publish(ev)
                        
