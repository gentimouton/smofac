from events import QuitEvent, CTickEvent
from pygame.locals import KEYDOWN, QUIT
import pygame


class InputController:
    """ Abstract controller class firing certain events when keys are pushed.
    No support for mouse clicks.
     
    The input controller of each mode should override input_map 
    with the appropriate key mappings.
    """

    input_map = {} # map keys to events; 
    #to be overriden by concrete input controllers

    def __init__(self, em):
        # no need to pygame.init(): events dont need any module  
        self._em = em
        self._em.subscribe(CTickEvent, self.on_tick)


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

                try:
                    ev = self.input_map[key]() # instantiate the event
                except KeyError: # key not associated with an event
                    pass

            # if the key generated a game event, send it          
            if ev:
                self._em.publish(ev)


