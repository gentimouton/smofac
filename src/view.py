from constants import RESOLUTION, BOARD_BGCOLOR, CELLSIZE, FONT_SIZE
from events import BoardBuiltEvent, BoardUpdatedEvent, RecipeMatchEvent
from pygame.sprite import LayeredDirty
from widgets import TextLabelWidget
import pygame




class PygameDisplay:
    
    def __init__(self, em):

        pygame.init() # OK to init multiple times
        
        self._em = em
        self._em.subscribe(BoardBuiltEvent, self.on_board_built)
        
        window = pygame.display.set_mode(RESOLUTION)
        self.window = window
        pygame.display.set_caption('Smoothie Factory')
        
        # blit the bg screen: all black
        bg = pygame.Surface(window.get_size()) 
        bgcolor = (0, 0, 0)
        bg.fill(bgcolor)
        bg = bg.convert()
        self.window_bg = bg 
        self.window.blit(bg, (0, 0))
        
        # build GUI
        self.gui = self._build_gui() # return a sprite group

        

    def _build_gui(self):
        """ Add a score widget on the right """
        
        gui = LayeredDirty() # only reblit when dirty=1
        
        # -- score at top-right of the window
        rec = pygame.Rect(400, 0, 100, FONT_SIZE * 1.5)
        evt_txt_dict = {RecipeMatchEvent: 'current_score'}
        score_widget = TextLabelWidget(self._em, '0',
                                       events_attrs=evt_txt_dict,
                                       rect=rec,
                                       txtcolor=(0, 0, 0),
                                       bgcolor=(255, 255, 255))
        gui.add(score_widget)
        
        return gui
    
    
    def on_board_built(self, ev):
        """ Build the board background. """
        
        width, height = ev.width, ev.height
        board = ev.board # to obtain cells from coords
        
        bg = pygame.Surface((width * CELLSIZE, height * CELLSIZE)) # TODO: crappy?
        bg = bg.convert()
        bg.fill(BOARD_BGCOLOR)
        
        for left in range(width):
            for top in range(height):
                cell = board.get_cell(left, top)
                bg.blit(cell.surf, cell.rect)
        
        self.board_bg = bg
        self.window.blit(bg, (0, 0))
        
        self._em.subscribe(BoardUpdatedEvent, self.on_board_update)

        
        
    def on_board_update(self, ev):
        """ Blit the background and the fruit sprites on the window. """

        #self.window.blit(self.window_bg, (0, 0))
        
        # board
        self.window.blit(self.board_bg, (0, 0))
        for fruit in ev.fruits:
            self.window.blit(fruit.surf, fruit.rect)
            
        # GUI
        gui = self.gui
        gui.clear(self.window, self.window_bg) # clear the window from all the sprites, replacing them with the bg
        gui.update() # calls update() on each sprite of the groups
        dirty_gui = gui.draw(self.window) #collect the display areas that need to be redrawn 
        pygame.display.update(dirty_gui) # redisplay those areas only
        
        # flip the screen
        pygame.display.flip()
    
