from config import font_size
from constants import FRUIT_COLORS
from events import MoveUpEvent, MoveDownEvent, MoveRightEvent, MoveLeftEvent, \
    ValidateEvent, VTickEvent
from pygame.font import Font
from pygame.locals import RLEACCEL, SRCALPHA
from pygame.rect import Rect
from pygame.sprite import DirtySprite
from pygame.surface import Surface
import logging
import pygame


# pygame inits
pygame.display.init() # OK to init multiple times
pygame.font.init()


class Widget(DirtySprite):
    """ abstract class for widgets """

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
        #self.image = Surface(self.rect.size) # needed?

        self.dirty = 1 # added [tho] 


    def on_textevent(self, event):
        """ Widget has to change its text. """
        evt_txt_attr = self.events_attrs[event.__class__]
        txt = str(getattr(event, evt_txt_attr))
        self.text = txt
        self.dirty = 1


    def update(self, duration):

        if self.dirty == 0:
            return

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

class MenuEntryWidget(TextLabelWidget):
    """ An entry in a menu widget. """

    def __init__(self, em, label, evt, rect,
                 ntxtcolor, nbgcolor, stxtcolor, sbgcolor,
                 evt_args=[]):
        """ ntxtcolor when non-selected, 
        stxtcolor when selected. 
        evt is the event to publish when the entry is pushed/executed.
        evt_args is the list of arguments needed to init the event.
        """
        TextLabelWidget.__init__(self, em, label, {}, rect,
                                 ntxtcolor, nbgcolor)
        self.stxtcolor = stxtcolor
        self.sbgcolor = sbgcolor
        self.ntxtcolor = ntxtcolor
        self.nbgcolor = nbgcolor
        self.exec_event = evt
        self.evt_args = evt_args
        # self.dirty set to 1 by TextLabelWidget

    def select(self):
        self.txtcolor = self.stxtcolor
        self.bgcolor = self.sbgcolor
        self.dirty = 1

    def unselect(self):
        self.txtcolor = self.ntxtcolor
        self.bgcolor = self.nbgcolor
        self.dirty = 1

    def execute(self):
        """ Publish the event this entry was associated with. """
        ev = self.exec_event(*self.evt_args)
        self._em.publish(ev)




class MenuWidget(Widget):
    """ A menu is made of several entries, each with a text label.
    """

    def __init__(self, em, evtlabels, rect=None,
                 ntxtcolor=(0, 0, 255), nbgcolor=(0, 0, 55),
                 stxtcolor=(0, 255, 0), sbgcolor=(0, 55, 0)):
        """ evtlabels is a list of (label, event to fire, evt creation args). 
        """
        Widget.__init__(self, em)

        #MoveDownEvent, MoveRightEvent, MoveLeftEvent
        self._em.subscribe(MoveUpEvent, self.on_prev)
        self._em.subscribe(MoveLeftEvent, self.on_prev)
        self._em.subscribe(MoveDownEvent, self.on_next)
        self._em.subscribe(MoveRightEvent, self.on_next)
        self._em.subscribe(ValidateEvent, self.on_validate)

        if not rect:
            # TODO: dimensions are hardcoded
            rect = Rect(0, 0, 100 + len(evtlabels) * 100, len(evtlabels) * 100)
        self.rect = rect

        self.entries = []
        for i, evtlabel in enumerate(evtlabels):
            if len(evtlabel) == 2: # event creation arguments not specified
                label, evt = evtlabel
                evt_args = []
            elif len(evtlabel) == 3: # event creation arguments specified
                label, evt, evt_args = evtlabel
            rec = Rect(i * 100, i * 100, 200, 50)
            entry = MenuEntryWidget(em, label, evt, rec,
                                    ntxtcolor, nbgcolor,
                                    stxtcolor, sbgcolor,
                                    evt_args)
            self.entries.append(entry)

        self.current_entry = 0
        try:
            self.entries[0].select()
        except IndexError: # labels was []
            logging.error('No entry labels were given to a menu widget.')
        self.dirty = 1


    def on_next(self, ev):
        """ Select next entry. """
        self.entries[self.current_entry].unselect()
        self.current_entry = (self.current_entry + 1) % len(self.entries)
        self.entries[self.current_entry].select()
        self.dirty = 1

    def on_prev(self, ev):
        """ Select previous entry """
        self.entries[self.current_entry].unselect()
        self.current_entry = (self.current_entry - 1) % len(self.entries)
        self.entries[self.current_entry].select()
        self.dirty = 1

    def on_validate(self, ev):
        """ Execute the selected entry """
        self.entries[self.current_entry].execute()


    def update(self, duration):
        """ reblit the entries on my rect """
        if self.dirty == 0:
            return

        # make the transparent box
        size = self.rect.size
        img = Surface(size, SRCALPHA)
        transparency = 50 # 0 = transparent, 255 = opaque
        img.fill((0, 0, 0, transparency))
        img = img.convert_alpha() # TODO: alpha or color key?

        # blit each entry
        for entry in self.entries:
            entry.update(duration)
            img.blit(entry.image, entry.rect)

        self.image = img
        #self.dirty = 0 # set by LayeredDirty







##################################


CPU_DISPLAY_FREQ = 2  # how many times per second to update the CPU display 

class CPUDisplayWidget(Widget):
    """ When receiving a tick event, display CPU consumption, 
    ie duration of work in the frame divided by total duration of the frame.
    """

    def __init__(self, em, text, rect=None, txtcolor=(255, 0, 0), bgcolor=None):
        """ text = to display at the start. """
        Widget.__init__(self, em)

        em.subscribe(VTickEvent, self.on_tick)
        self.display_timer = 1000 / CPU_DISPLAY_FREQ # in millis

        # gfx
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


    def on_tick(self, ev):
        """ Widget has to change its text. """
        total = ev.loopduration
        self.display_timer -= total
        if self.display_timer > 0:
            return

        self.display_timer = 1000 / CPU_DISPLAY_FREQ # in millis
        work = ev.workduration
        try:
            self.text = 'CPU: %2d %%' % (int(100 * work / total))
        except ZeroDivisionError:
            self.text = '0'
        self.dirty = 1 # schedule for reblit


    def update(self, duration):
        """ Reblit text if dirty. """
        if self.dirty == 0:
            return

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


########################################    

class RecipesWidget(Widget):

    def __init__(self, em, recipes, events_attrs={}, rect=None,
                 txtcolor=None, bgcolor=None):
        """ Representation of the recipes and their score.
        When receiving a recipe match event, blink the recipe.
        events_attrs maps event classes to recipe attributes. 
        Usage: RecipesWidget(em, recipes_to_display, {EventName: 'recipe_attr'})
        recipes maps tuples of fruit type to their score.  
        """

        Widget.__init__(self, em)

        # subscribe to recipe match events
        self.events_attrs = events_attrs
        for evtClass in events_attrs:
            self._em.subscribe(evtClass, self.on_recipe_match)

        self.recipes = recipes

        # sort recipes by length, then score, then color 
        ord_recipes = list(zip(recipes.keys(), recipes.values()))
        ord_recipes.sort(key=lambda pair: (len(pair[0]), pair[1], pair[0][0]))

        # gfx
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
        self.recipe_lines = {}
        recipe_num = 0
        for recipe, score in ord_recipes:
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
            recipe_line = {'score':score, 'rect': line_rect}
            self.recipe_lines[recipe] = recipe_line

            widget_surf.blit(line_surf, line_rect)
            recipe_num += 1

        self.image = widget_surf.convert()


    def on_recipe_match(self, event):
        """ TODO: Highlight the recipe that just got matched. """
        evt_recipe_attr = self.events_attrs[event.__class__]
        recipe = str(getattr(event, evt_recipe_attr))


    def update(self, duration):
        """ Nothing to do, really ...
        But widgets in sprite groups need this method.
        """
        pass
