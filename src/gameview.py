from config import bg_color, resolution, font_size, steps_per_cell
from events import BoardBuiltEvent, BoardUpdatedEvent, RecipeMatchEvent, \
    GameBuiltEvent, VTickEvent, FruitKilledEvent, FruitSpeedEvent, FruitPlacedEvent, \
    QuitEvent
from fruitspr import FruitSpr
from pygame.rect import Rect
from pygame.sprite import LayeredDirty
from pygame.surface import Surface
from widgets import TextLabelWidget, RecipesWidget, CPUDisplayWidget
import pygame


class GameView:

    def __init__(self, em, ev):
        """ Score and recipe widgets on the right, game board on the left.
        em is the mode's event manager,
        ev is an event containing data from the previous mode (e.g. menu 
        or level transition). ev contains the level number.  
        """

        pygame.display.init() # OK to init multiple times
        pygame.font.init()

        self._em = em

        window = pygame.display.set_mode(resolution)
        self.window = window
        pygame.display.set_caption('Smoothie Factory - In Play')

        # blit the bg screen: all black
        bg = Surface(window.get_size())
        bg.fill((0, 0, 0))
        bg = bg.convert()
        self.window_bg = bg
        self.window.blit(bg, (0, 0))

        # fruit sprites 
        self.fruit_to_spr = {} # map a fruit to its sprite
        self.fruit_sprites = LayeredDirty() # only reblit when dirty=1
        self.interp_steps = 0 # 2 interpolation steps between 2 model updates

        # build GUI
        self.gui = self._build_gui() # return a sprite group

        em.subscribe(BoardBuiltEvent, self.on_board_built)
        em.subscribe(GameBuiltEvent, self.on_game_built)
        em.subscribe(FruitKilledEvent, self.on_fruit_killed)
        em.subscribe(FruitPlacedEvent, self.on_fruit_spawned)
        em.subscribe(FruitSpeedEvent, self.on_speed_change)
        em.subscribe(QuitEvent, self.on_quit)

    def _build_gui(self):
        """ Add a score widget on the right """

        gui = LayeredDirty() # only reblit when dirty=1

        # score at top-right of the window
        rec = Rect(600 + 10, 0,
                   100, font_size * 1.5)
        evt_txt_dict = {RecipeMatchEvent: 'current_score'}
        score_widget = TextLabelWidget(self._em, '0',
                                       events_attrs=evt_txt_dict,
                                       rect=rec,
                                       txtcolor=(0, 0, 0),
                                       bgcolor=(222, 222, 222))
        gui.add(score_widget)

        # CPU at bottom-right of the window
        rec = Rect(600 + 10, 600 - font_size * 1.5,
                   100, font_size * 1.5)
        cpu_widget = CPUDisplayWidget(self._em, '0',
                                      rect=rec,
                                      txtcolor=(0, 0, 0),
                                      bgcolor=(222, 222, 222))
        gui.add(cpu_widget)


        # the recipe widget added when the game is built
        return gui



    def on_game_built(self, ev):
        """ Build the recipe GUI, and set the spr movement timer. """

        # recipe widget
        evt_recipe_dict = {RecipeMatchEvent: 'recipe'}
        rec = Rect(600, font_size * 1.5, 150, 400)
        # ev.recipes maps tuples of fruit type to score
        rwid = RecipesWidget(self._em,
                             ev.recipes,
                             evt_recipe_dict,
                             rect=rec,
                             txtcolor=(222, 222, 222),
                             bgcolor=(0, 0, 0))
        self.gui.add(rwid)

        # spr movement timer
        model_mvt_timer = 1000 / ev.fruit_speed
        self.base_spr_timer = model_mvt_timer / steps_per_cell
        self.spr_timer = self.base_spr_timer

        self._em.subscribe(VTickEvent, self.on_tick)


    def on_board_built(self, ev):
        """ Build the board background. """

        width, height = ev.width, ev.height
        board = ev.board # to obtain cells from coords

        win_height = self.window.get_height()
        bg = Surface((win_height, win_height))
        bg = bg.convert()
        bg.fill(bg_color)

        for left in range(width):
            for top in range(height):
                cell = board.get_cell(left, top)
                bg.blit(cell.image, cell.rect)
        # blit the board bg onto the window's bg
        self.window_bg.blit(bg, (0, 0))

        self._em.subscribe(BoardUpdatedEvent, self.on_board_update)



    def on_fruit_spawned(self, ev):
        """ When a fruit appears, add it to the sprite group """
        fruit = ev.fruit
        fruit_spr = FruitSpr(fruit, self.interp_steps)
        self.fruit_to_spr[fruit] = fruit_spr
        self.fruit_sprites.add(fruit_spr)

    def on_fruit_killed(self, ev):
        """ When a fruit is killed, remove the spr """
        fruit = ev.fruit
        fruit_spr = self.fruit_to_spr[fruit]
        fruit_spr.kill() # remove fruit_spr from self.fruit_sprites
        del self.fruit_to_spr[fruit]


    def on_board_update(self, ev):
        """ Store the new fruits' positions. 
        The actual display happens at clock tick. 
        """
        # prepare spr interpolation timer and step counter
        self.spr_timer = self.base_spr_timer
        self.interp_steps = 0 # restart interpolating fruit positions
        for fruit_spr in self.fruit_sprites:
            fruit_spr.resync(self.interp_steps)


    def on_tick(self, ev):
        """ Blit the active board elements and the GUI on the screen. """

        if not pygame.display.get_init(): # if the display is ON 
            return

        # spr positions
        duration = ev.loopduration
        self.spr_timer -= duration
        if self.spr_timer <= 0:
            self.spr_timer = self.base_spr_timer
            self.interp_steps += 1
            # interpolate 3 positions, 
            # but the last one is done when board is updated (so only 2)
            if self.interp_steps < steps_per_cell:
                for fruit in self.fruit_sprites:
                    fruit.resync(self.interp_steps)

        # display    
        gui = self.gui
        fruits = self.fruit_sprites
        screen = self.window
        bg = self.window_bg
        # clear the window from all the sprites, replacing them with the bg
        gui.clear(screen, bg)
        fruits.clear(screen, bg)
        gui.update(duration) # call update() on each sprite of the group
        fruits.update(duration) # reset the dirty flag to 0
        #collect the display areas that need to be redrawn
        dirty_gui = gui.draw(screen)
        dirty_fruits = fruits.draw(screen)
        dirty_rects = dirty_gui + dirty_fruits
        pygame.display.update(dirty_rects) # redisplay those areas only

        # flip the screen
        pygame.display.flip()


    def on_speed_change(self, ev):
        """ When the fruit speed changes, update the speed of fruit sprites. """
        model_mvt_timer = 1000 / ev.speed
        self.base_spr_timer = model_mvt_timer / steps_per_cell


    def on_quit(self, ev):
        """ Shut down the display """
        pygame.display.quit()
