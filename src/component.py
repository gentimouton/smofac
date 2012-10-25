from constants import FPS, RESOLUTION
from mode import Mode
from events import CTickEvent, MTickEvent, VTickEvent, QuitEvent, QuitEvent, \
    VTickEvent, ToGameEvent, ValidateEvent, MoveUpEvent, MoveDownEvent, \
    MoveLeftEvent, MoveRightEvent
from pygame.locals import KEYDOWN, K_ESCAPE, QUIT, K_SPACE, K_EQUALS, K_PLUS, \
    K_MINUS, K_UNDERSCORE, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_RETURN
from pygame.rect import Rect
from pygame.sprite import LayeredDirty, LayeredDirty
from pygame.surface import Surface
from time import sleep, time
from widgets import MenuWidget, MenuWidget
import pygame




class InputController:

    input_map = {} # map keys to events

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


##########################################################################


class MenuDisplay:

    # default view menu: a single quit button
    evtlabels = [('default quit', QuitEvent)
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
        