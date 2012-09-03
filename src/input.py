from events import QuitEvent, TriggerTrapEvent, TickEvent, PRIO_TICK_INPUT
from pygame.locals import KEYDOWN, K_ESCAPE, QUIT, K_SPACE
import logging
import pygame



class InputController:

    def __init__(self, em):
        pygame.init() # OK to init multiple times
        self._em = em
        self._em.subscribe(TickEvent, self.on_tick, PRIO_TICK_INPUT)
        

    def on_tick(self, tickevt):
        """ Every clock tick, handle input events from the keyboard. """
        
        for pevent in pygame.event.get():
            ev = None
            
            # click on the window's X to close it
            if pevent.type == QUIT:
                ev = QuitEvent()
                
            # keyboard events
            elif pevent.type == KEYDOWN:
                key = pevent.key
                
                if key == K_ESCAPE:
                    ev = QuitEvent()
                
                elif key == K_SPACE:
                    ev = TriggerTrapEvent()
            
            # if the pygame event generated a game event, send it          
            if ev:
                self._em.publish(ev)
