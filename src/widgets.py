from constants import FONT_SIZE, FRUIT_COLORS
from pygame.font import Font
from pygame.locals import RLEACCEL, SRCALPHA
from pygame.rect import Rect
from pygame.sprite import DirtySprite
from pygame.surface import Surface
import logging


class Widget(DirtySprite):
    """ abstract class for other types of widgets """

    def __init__(self, em):
        DirtySprite.__init__(self)
        self._em = em
        self.dirty = 1


############################################################################


class TextLabelWidget(Widget):
    """ display static text """ 
    
    def __init__(self, em, text, events_attrs={}, rect=None,
                 txtcolor=(255, 0, 0), bgcolor=None):
        """ When receiving an event containing text, 
        replace self.text by that event's text.
        events_attrs maps event classes to event text attributes. 
        Usage: TextLabelWidget(em, 'start text', {EventName: 'evt_attr'})  
        """
        Widget.__init__(self, em)
        
        self.events_attrs = events_attrs
        for evtClass in events_attrs:
            self._em.subscribe(evtClass, self.on_textevent)
        
        # gfx
        font_size = FONT_SIZE
        self.font = Font(None, font_size)
        if rect:
            self.rect = rect
        else:
            self.rect = Rect((0, 0), (100, font_size + 4)) 
            #default width = 100px,
            # 4px from 1px each of border bottom,
            # padding bottom, padding top, and border top 
                
        self.txtcolor = txtcolor
        self.bgcolor = bgcolor

        self.text = text
        self.image = Surface(self.rect.size)
        
    
    def set_text(self, text):
        self.text = text
        self.dirty = 1

    def get_text(self):
        return self.text
    

    def on_textevent(self, event):
        """ Widget has to change its text. """        
        evt_txt_attr = self.events_attrs[event.__class__]
        txt = str(getattr(event, evt_txt_attr))
        self.set_text(txt)
        
        
    def update(self):
        
        if self.dirty == 0:
            return
        
        # TODO: is bliting on existing surf faster than creating a new surface?
        size = self.rect.size
        txtcolor = self.txtcolor
        bgcolor = self.bgcolor
        if bgcolor: # opaque bg
            txtimg = self.font.render(self.text, True, txtcolor, bgcolor)
            txtimg = txtimg.convert()
            img = Surface(size)
            img.fill(bgcolor)
        else: # transparent bg
            txtimg = self.font.render(self.text, True, txtcolor)
            txtimg = txtimg.convert_alpha()
            img = Surface(size, SRCALPHA) # handle transparency
            img.fill((0, 0, 0, 0)) # 0 = transparent, 255 = opaque
        
        # center the txt inside its box
        ctr_y = size[1] / 2
        textpos = txtimg.get_rect(left=2, centery=ctr_y)
        img.blit(txtimg, textpos)
        self.image = img
        
        #self.dirty = 0 # no need to set to 0: this is done by LayeredDirty
        

##################################

class RecipesWidget(Widget):

    def __init__(self, em, recipes, events_attrs={}, rect=None,
                 txtcolor=None, bgcolor=None):
        """ Representation of the recipes and their score.
        When receiving a recipe match event, blink the recipe.
        events_attrs maps event classes to recipe attributes. 
        Usage: RecipesWidget(em, recipes_to_display, {EventName: 'recipe_attr'})  
        """

        Widget.__init__(self, em)
        
        # subscribe to recipe match events
        self.events_attrs = events_attrs
        for evtClass in events_attrs:
            self._em.subscribe(evtClass, self.on_recipe_match)
        
        self.recipes = recipes
        
        # gfx
        font_size = FONT_SIZE
        self.font = Font(None, font_size)
        if rect:
            self.rect = rect
        else:
            self.rect = Rect((0, 0), (100, font_size + 4)) 
            #default width = 100px,
            # 4px from 1px each of border bottom,
            # padding bottom, padding top, and border top 
        
        self.txtcolor = txtcolor
        self.bgcolor = bgcolor
        
        # widget surface
        widget_surf = Surface(self.rect.size)
        
        # recipe lines
        self.recipe_lines = []
        recipe_num = 0
        for recipe, score in recipes.items():
            # blit fruit surfs and recipe surf on line surf
            line_rect = Rect(0, recipe_num * font_size + 10, # 10px between lines
                             self.rect.width, font_size)
            line_surf = Surface(line_rect.size)
            
            # score surf
            score_surf = self.font.render(str(score), True, txtcolor, bgcolor)
            score_rect = Rect(line_rect.width - 30, 0,
                              10, line_rect.height)
            line_surf.blit(score_surf, score_rect)
            
            # fruits surf
            fruit_size = int(font_size * 0.75)
            for fruit_num, fruit in enumerate(recipe):
                fruit_color = FRUIT_COLORS[fruit]
                fruit_rect = Rect(fruit_num * (fruit_size + 5), 0, # 5px-interspace 
                                  fruit_size, fruit_size)
                fruit_surf = Surface(fruit_rect.size)
                fruit_surf.fill(fruit_color)
                line_surf.blit(fruit_surf, fruit_rect)
            
            # store the line so that we can blink/reblit it
            recipe_line = {'recipe': recipe, 'score':score, 'rect': line_rect}
            self.recipe_lines.append(recipe_line) 
                
            widget_surf.blit(line_surf, line_rect)
            recipe_num += 1
            
        self.image = widget_surf.convert()
            

    def on_recipe_match(self, event):
        """ Highlight the recipe that just got matched. """        
        evt_recipe_attr = self.events_attrs[event.__class__]
        recipe = str(getattr(event, evt_recipe_attr))
        logging.info('Should blink %s' % str(recipe))
        
        
    def update(self):
        
        if self.dirty == 0:
            return
        
        # TODO: is bliting on existing surf faster than creating a new surface?
        
        #self.dirty = 0 # no need to set to 0: this is done by LayeredDirty
