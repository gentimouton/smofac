from config import spawn_period, rng_seed
from constants import FRUIT_LIST
from events import FruitSpawnedEvent, CTickEvent
from fruit import Fruit
import logging
import random

class Spawner():
    def __init__(self, em, cell):
        self.rng = random.Random()
        self.rng.seed(rng_seed) # determinism = easier to debug
        self.spawn_timer = 0 # start spawning right away 
        self.fruits_spawned = 0 # ++ when a fruit appears
        self.cell = cell 
        self._em = em
        em.subscribe(CTickEvent, self.on_tick)
        
        
    def on_tick(self, ev):
        """ Spawn a fruit if it's time to do it. """
        
        duration = ev.loopduration
        self.spawn_timer -= duration
        if self.spawn_timer <= 0:
            random_int = self.rng.randint(0, len(FRUIT_LIST) - 1)
            fruit_type = FRUIT_LIST[random_int]
            fruit = Fruit(fruit_type, self.fruits_spawned)
            self.spawn_timer = spawn_period * 1000
            self.fruits_spawned += 1
            logging.debug('spawned Fruit %s' % fruit)
            ev = FruitSpawnedEvent(fruit)
            self._em.publish(ev)
                                        
