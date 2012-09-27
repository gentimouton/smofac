from clock import Clock
from constants import RESOLUTION, FONT_SIZE
from events import TickEvent, QuitEvent, EventManager
from input import InputController
from pygame.rect import Rect
from pygame.sprite import LayeredDirty
from pygame.surface import Surface
from widgets import MenuWidget
import logging
import pygame

class MenuDisplay:
    
    def __init__(self, em):

        pygame.display.init() # OK to init multiple times
        pygame.font.init()
        
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

        em.subscribe(TickEvent, self.on_tick)
        em.subscribe(QuitEvent, self.on_quit)

        
    def _build_gui(self):
        """ Make a menu widget. """
        gui = LayeredDirty() # only reblit when dirty=1
        evtlabels = [('quit1', QuitEvent),
                     ('quit2', QuitEvent),
                     ('quit3', QuitEvent),
                     ('quit4', QuitEvent)]
        # TODO: prepare a rect
        menu_widget = MenuWidget(self._em, evtlabels)
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
        
        
        
    
def main():
    logging.basicConfig(level=logging.INFO)
    em = EventManager()
    view = MenuDisplay(em)
    keyboard = InputController(em)
    clock = Clock(em)
    clock.start() # start the main loop
    
if __name__ == "__main__":
    main()
    
    
