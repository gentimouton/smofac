from constants import RESOLUTION, BOARD_BGCOLOR, CELLSIZE, FONT_SIZE
from events import BoardBuiltEvent, BoardUpdatedEvent, RecipeMatchEvent, \
    GameBuiltEvent, TickEvent
from pygame.sprite import LayeredDirty
from widgets import TextLabelWidget, RecipesWidget
import logging
import pygame



class PygameDisplay:
    
    def __init__(self, em):

        pygame.init() # OK to init multiple times
        
        self._em = em
        
        window = pygame.display.set_mode(RESOLUTION)
        self.window = window
        pygame.display.set_caption('Smoothie Factory')
        
        # blit the bg screen: all black
        bg = pygame.Surface(window.get_size()) 
        bg.fill((0, 0, 0))
        bg = bg.convert()
        self.window_bg = bg 
        self.window.blit(bg, (0, 0))
        
        # build GUI
        self.fruit_sprites = LayeredDirty() # only reblit when dirty=1
        self.gui = self._build_gui() # return a sprite group

        em.subscribe(TickEvent, self.on_tick)
        em.subscribe(BoardBuiltEvent, self.on_board_built)
        em.subscribe(GameBuiltEvent, self.on_game_built)
        
        
        
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
        
        # TODO: should make and add an empty recipe widget?
         
        return gui
    
    
    
    def on_game_built(self, ev):
        """ build the recipe GUI """
        
        evt_recipe_dict = {RecipeMatchEvent: 'recipe'}
        rec = pygame.Rect(400, 60, 150, 400)
        recipe_widget = RecipesWidget(self._em, 
                                      ev.recipes, 
                                      evt_recipe_dict, 
                                      rect=rec, 
                                      txtcolor=(222,222,222), 
                                      bgcolor=(0,0,0))
        self.gui.add(recipe_widget)
        
        
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
                bg.blit(cell.image, cell.rect)
        # blit the board bg onto the window's bg
        self.window_bg.blit(bg, (0,0))
        
        self._em.subscribe(BoardUpdatedEvent, self.on_board_update)

        
        
    def on_board_update(self, ev):
        """ Store the new fruits' positions. 
        The actual display happens at clock tick. 
        """
        for fruit in ev.fruits:
            self.fruit_sprites.add(fruit)
        

        
    def on_tick(self, ev):
        """ Blit the board (+ fruits and traps) and the GUI on the screen. """
        
        # board
        for fruit in self.fruit_sprites:# TODO: should be a dirty group
            self.window.blit(fruit.image, fruit.rect)
    
        # GUI
        gui = self.gui
        fruits = self.fruit_sprites
        gui.clear(self.window, self.window_bg) # clear the window from all the sprites, replacing them with the bg
        fruits.clear(self.window, self.window_bg)
        gui.update() # calls update() on each sprite of the groups
        fruits.update()
        dirty_gui = gui.draw(self.window) #collect the display areas that need to be redrawn 
        dirty_fruits = fruits.draw(self.window)
        dirty_rects = dirty_gui + dirty_fruits
        pygame.display.update(dirty_rects) # redisplay those areas only
        
        # flip the screen
        pygame.display.flip()
