from constants import FONT_SIZE
from pygame.font import Font
from pygame.locals import RLEACCEL, SRCALPHA
from pygame.rect import Rect
from pygame.sprite import DirtySprite
from pygame.surface import Surface, Surface


class Widget(DirtySprite):
    """ abstract class for other types of widgets """

    def __init__(self, em):
        DirtySprite.__init__(self)
        self._em = em
        self.dirty = 1


############################################################################


class TextLabelWidget(Widget):
    """ display static text """ 
    
    def __init__(self, em, text, events_attrs=[], rect=None,
                 txtcolor=(255, 0, 0), bgcolor=None):
        """ When receiving an event containing text, 
        replace self.text by that event's text.
        events_attrs maps event classes to event text attributes. 
        Usage: TextLabelWidget(em, 'start text', {EventName: 'evt_attr'})  
        """
        Widget.__init__(self, em)
        
        self.events_attrs = events_attrs
        if events_attrs:
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
        
        