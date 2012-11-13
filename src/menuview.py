from config import resolution
from events import QuitEvent, VTickEvent
from pygame.sprite import LayeredDirty
from pygame.surface import Surface
from widgets import MenuWidget
import pygame



class MenuView:

    # default view menu: a single quit button
    evtlabels = [('default quit', QuitEvent)
                 ]
    
    pagename = '' # to be displayed at the top of the window 

    def __init__(self, em, ev):
        """ em is the mode's event manager,
        ev is an event containing data from the previous mode. 
        """

        self._em = em

        window = pygame.display.set_mode(resolution)
        self.window = window
        pygame.display.set_caption('Smoothie Factory - %s' % self.pagename)

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
        gui.update(ev.loopduration) # call update() on each sprite of the group
        #collect the display areas that need to be redrawn
        dirty_gui = gui.draw(screen)
        dirty_rects = dirty_gui
        pygame.display.update(dirty_rects) # redisplay those areas only
        # flip the screen
        pygame.display.flip()
        
        