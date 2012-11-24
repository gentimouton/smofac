from events import FruitSpawnedEvent, CTickEvent
from fruit import Fruit
import logging
import random



class Spawner():
    def __init__(self, em, cell, fruit_names, seed, spawn_period):
        self.fruits = fruit_names
        self.rng = random.Random()
        self.rng.seed(seed)
        self.spawn_period = spawn_period
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
            random_int = self.rng.randint(0, len(self.fruits) - 1)
            fruit_type = self.fruits[random_int]
            fruit = Fruit(fruit_type, self.fruits_spawned)
            self.spawn_timer = self.spawn_period * 1000
            self.fruits_spawned += 1
            logging.debug('spawned Fruit %s' % fruit)
            ev = FruitSpawnedEvent(fruit)
            self._em.publish(ev)
                                        
