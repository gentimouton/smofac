from events import QuitEvent, TriggerTrapEvent, TickEvent, PRIO_TICK_CTRL, \
    AccelerateFruitsEvent, DecelerateFruitsEvent
from pygame.locals import KEYDOWN, K_ESCAPE, QUIT, K_SPACE, K_EQUALS, K_PLUS, \
    K_MINUS, K_UNDERSCORE
import logging
import pygame



class InputController:

    def __init__(self, em):
        # no need to pygame.init() before: events dont need any module  
        self._em = em
        self._em.subscribe(TickEvent, self.on_tick, PRIO_TICK_CTRL)
        

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
                    
                elif key in (K_EQUALS, K_PLUS):
                    # accelerate the speed of the fruits
                    ev = AccelerateFruitsEvent()
                elif key in (K_MINUS, K_UNDERSCORE):
                    ev = DecelerateFruitsEvent()
            
            # if the pygame event generated a game event, send it          
            if ev:
                self._em.publish(ev)
