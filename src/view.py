from constants import RESOLUTION, BG_COLOR, CELLSIZE, FONT_SIZE
from events import BoardBuiltEvent, BoardUpdatedEvent, RecipeMatchEvent, \
    GameBuiltEvent, TickEvent, FruitKilledEvent
from pygame.sprite import LayeredDirty
from widgets import TextLabelWidget, RecipesWidget, CPUDisplayWidget
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
        em.subscribe(FruitKilledEvent, self.on_fruit_kill)
        
        
        
    def _build_gui(self):
        """ Add a score widget on the right """
        
        gui = LayeredDirty() # only reblit when dirty=1
        
        # score at top-right of the window
        rec = pygame.Rect(600 + 10, 0,
                          100, FONT_SIZE * 1.5)
        evt_txt_dict = {RecipeMatchEvent: 'current_score'}
        score_widget = TextLabelWidget(self._em, '0',
                                       events_attrs=evt_txt_dict,
                                       rect=rec,
                                       txtcolor=(0, 0, 0),
                                       bgcolor=(222, 222, 222))
        gui.add(score_widget)
        
        # CPU at bottom-right of the window
        rec = pygame.Rect(600 + 10, 600 - FONT_SIZE * 1.5,
                          100, FONT_SIZE * 1.5)
        cpu_widget = CPUDisplayWidget(self._em, '0',
                                      rect=rec,
                                      txtcolor=(0, 0, 0),
                                      bgcolor=(222, 222, 222))
        gui.add(cpu_widget)
        
        
        # the recipe widget added when the game is built
        return gui
    
    
    
    def on_game_built(self, ev):
        """ build the recipe GUI """
        
        evt_recipe_dict = {RecipeMatchEvent: 'recipe'}
        rec = pygame.Rect(600, FONT_SIZE * 1.5, 150, 400)
        # ev.recipes maps tuples of fruit type to score
        recipe_widget = RecipesWidget(self._em,
                                      ev.recipes,
                                      evt_recipe_dict,
                                      rect=rec,
                                      txtcolor=(222, 222, 222),
                                      bgcolor=(0, 0, 0))
        self.gui.add(recipe_widget)
        
        
    def on_board_built(self, ev):
        """ Build the board background. """
        
        width, height = ev.width, ev.height
        board = ev.board # to obtain cells from coords
        #(width * CELLSIZE, height * CELLSIZE)
        
        win_height = self.window.get_height()
        bg = pygame.Surface((win_height, win_height))
        bg = bg.convert()
        bg.fill(BG_COLOR)
        
        for left in range(width):
            for top in range(height):
                cell = board.get_cell(left, top)
                bg.blit(cell.image, cell.rect)
        # blit the board bg onto the window's bg
        self.window_bg.blit(bg, (0, 0))
        
        self._em.subscribe(BoardUpdatedEvent, self.on_board_update)

        
        
    def on_board_update(self, ev):
        """ Store the new fruits' positions. 
        The actual display happens at clock tick. 
        """
        for fruit in ev.fruits:
            self.fruit_sprites.add(fruit)
    
    def on_fruit_kill(self, ev):
        """ When a fruit is killed, remove the spr """
        fruit = ev.fruit
        fruit.kill()
        del fruit # needed?
        
                
    def on_tick(self, ev):
        """ Blit the active board elements and the GUI on the screen. """
            
        gui = self.gui
        fruits = self.fruit_sprites
        # clear the window from all the sprites, replacing them with the bg
        gui.clear(self.window, self.window_bg) 
        fruits.clear(self.window, self.window_bg)
        gui.update() # call update() on each sprite of the group
        fruits.update()
        #collect the display areas that need to be redrawn
        dirty_gui = gui.draw(self.window)  
        dirty_fruits = fruits.draw(self.window)
        dirty_rects = dirty_gui + dirty_fruits
        pygame.display.update(dirty_rects) # redisplay those areas only
        
        # flip the screen
        pygame.display.flip()
