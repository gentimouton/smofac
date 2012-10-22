from collections import defaultdict, deque
from clock import Clock
from constants import RESOLUTION, FONT_SIZE
from events import QuitEvent, EventManager, VTickEvent
from input import InputController
from pygame.rect import Rect
from pygame.sprite import LayeredDirty
from pygame.surface import Surface
from widgets import MenuWidget
import logging
import pygame


pygame.display.init()


class SwitchViewEvent():
    pass
    
    
class MainDisplay(EventManager):
    """ Handles transitions between views
    and acts as an event broker 
    between the current view and the main event manager.
    """
    
    def __init__(self, em):
        self._em = em

        # map events to their callbacks
        self._callbacks = defaultdict(set)
        
        # FSM of views
        fsm = {
               'v1': {
                      'viewtype':MenuDisplay1,
                      'transitions': {SwitchViewEvent: 'v2'}
                      },
               'v2': {
                      'viewtype':MenuDisplay2,
                      'transitions': {SwitchViewEvent: 'v1'}
                      },
               }
        self._fsm = fsm
        em.subscribe(SwitchViewEvent, self.on_switchview)
        
        # the view registers to new events by itself
        self.cur_view_name = 'v1'
        self.cur_view = MenuDisplay1(self)
        
        
        
    def subscribe(self, ev_class, callback):
        """ Register the callback from a view component,
        and subscribe to that event from the main event manager.
        """
        self._callbacks[ev_class].add(callback)
        self._em.subscribe(ev_class, self.forward_evt)
        
    
    def join_new_listeners(self):
        pass

    
    def forward_evt(self, event):
        """ Forward an event from the main event manager
        to the view components who subscribed to it.
        """
        for cb in self._callbacks[event.__class__]:
            cb(event)
        
        
    def publish(self, event):
        """ Forward an event from a view component to the main event manager """
        self._em.publish(event)
        
        
    def on_switchview(self, ev):
        self._callbacks.clear()
        if self.cur_view_name == 'v1':
            self.cur_view = MenuDisplay2(self)
            self.cur_view_name = 'v2' 
        else:
            self.cur_view = MenuDisplay1(self)
            self.cur_view_name = 'v1'
        
        
        
        
        
class MenuDisplay:
    
    # default view menu: a single quit button
    evtlabels = [('quit',QuitEvent)
                 ] 

    def __init__(self, em):

        self._em = em

        window = pygame.display.set_mode(RESOLUTION)
        self.window = window
        pygame.display.set_caption('Smoothie Factory')

        # blit the bg screen: all black
        bg = Surface(window.get_size())
        bg.fill((0, 0, 0))
        bg = bg.convert()
        self.window_bg = bg
        self.window.blit(bg, (0, 0))

        # build GUI
        self.gui = self._build_gui() # return a sprite group

        em.subscribe(VTickEvent, self.on_tick)
        em.subscribe(QuitEvent, self.on_quit)


    def _build_gui(self):
        """ Make a menu widget. """
        gui = LayeredDirty() # only reblit when dirty=1
        # TODO: prepare a rect
        menu_widget = MenuWidget(self._em, self.evtlabels)
        gui.add(menu_widget)
        return gui


    def on_tick(self, ev):
        """ Blit the active board elements and the GUI on the screen. """

        if not pygame.display.get_init(): # if the display is ON 
            return

        gui = self.gui
        screen = self.window
        bg = self.window_bg
        # clear the window from all the sprites, replacing them with the bg
        gui.clear(screen, bg)
        duration = ev.loopduration
        gui.update(duration) # call update() on each sprite of the group
        #collect the display areas that need to be redrawn
        dirty_gui = gui.draw(screen)
        dirty_rects = dirty_gui
        pygame.display.update(dirty_rects) # redisplay those areas only
        # flip the screen
        pygame.display.flip()

    def on_quit(self, ev):
        """ Shut down the display """
        pygame.display.quit()


class MenuDisplay1(MenuDisplay):
    evtlabels = [('switch', SwitchViewEvent),
                 ('quit', QuitEvent),
                 ('switch2', SwitchViewEvent),
                 ('quit2', QuitEvent)
                 ]

class MenuDisplay2(MenuDisplay):
    evtlabels = [('back', SwitchViewEvent),
                 ('quit', QuitEvent)
                 ]
        



def main():
    logging.basicConfig(level=logging.INFO)
    em = EventManager()

    view = MainDisplay(em)
    keyboard = InputController(em)
    clock = Clock(em)
    clock.start() # start the main loop

if __name__ == "__main__":
    main()


