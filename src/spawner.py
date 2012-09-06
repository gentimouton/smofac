from constants import SPAWNFREQ, RNGSEED, FRUIT_LIST
from events import FruitSpawnedEvent
from fruit import Fruit
import logging
import random

class Spawner():
    def __init__(self, em, cell):
        self.rng = random.Random()
        self.rng.seed(RNGSEED) # determinism = easier to debug
        self.spawn_timer = SPAWNFREQ # spawn fruits every X frames 
        self.fruits_spawned = 0 # ++ when a fruit appears
        self.cell = cell 
        self._em = em
        
        
    def tick(self, elapsed_millis):
        """ Spawn a fruit if it's time to do it. 
        Return (a, b), where a is whether it had to spawn,
        and b the fruit (if succeeded).
        elapsed_millis is the time elapsed since last tick.
        """
        
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            if self.cell.fruit: # should spawn new fruit, but can't: game over!
                return True, None
            else: # can spawn: game keeps going
                random_int = self.rng.randint(0, len(FRUIT_LIST) - 1)
                fruit_type = FRUIT_LIST[random_int]
                fruit = Fruit(self.cell, fruit_type, self.fruits_spawned)
                self.cell.fruit = fruit
                self.spawn_timer = SPAWNFREQ
                self.fruits_spawned += 1
#                logging.debug('spawned fruit#%d - %s, now have fruits %s' 
#                             % (fruit_id, fruit_type, ','.join([str(k) for k in self.fruits.keys()])))
                ev = FruitSpawnedEvent(fruit)
                self._em.publish(ev)
                return True, fruit # no game over
        
        return False, None
