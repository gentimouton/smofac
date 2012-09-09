from constants import FRUIT_COLORS, FONT_SIZE, CELLSIZE
from pygame.font import Font
from pygame.rect import Rect
from pygame.sprite import DirtySprite
from pygame.surface import Surface


LOOPING = 'looping' # in the board loop
LEAVING = 'leaving' # on (or scheduled for) the exit path, 
WAITING = 'waiting' # standing still


class Fruit(DirtySprite):
    
    def __init__(self, cell_coords, fruit_type, fruit_num):
        self.fruit_type = fruit_type # 'S' for strawberry
        self.fruit_num = fruit_num
        self.state = LOOPING
        
        # graphics
        DirtySprite.__init__(self)
        self.dirty = 1 # when 1, the view will blit it. 
        # dirty is set to 0 by the LayeredDirty sprite group it belongs to.

        # fill with color and write fruit number 
        self.image = Surface((CELLSIZE * 4 / 5, CELLSIZE * 4 / 5))
        self.image.fill(FRUIT_COLORS[fruit_type])
        self.font = Font(None, FONT_SIZE) 
        txtsurf = self.font.render(str(fruit_num), True, (0, 0, 0))
        textpos = txtsurf.get_rect(centerx=self.image.get_width() / 2,
                                   centery=self.image.get_height() / 2)
        self.image.blit(txtsurf, textpos)

        self.move_to(cell_coords)
        
    
    def __repr__(self):
        return '%s#%d %s' % (self.fruit_type,
                                self.fruit_num,
                                self.state)
    def __str__(self):
        return self.__repr__()
        
    @property
    def is_leaving(self):
        return self.state == LEAVING
    def leave(self):
        self.state = LEAVING
    @property
    def is_waiting(self):
        return self.state == WAITING
    def wait(self):
        self.state = WAITING 
    def loop(self):
        self.state = LOOPING
    
    def move_to(self, cell_coords):
        left, top = cell_coords
        self.rect = Rect(left * CELLSIZE + CELLSIZE / 10 ,
                         top * CELLSIZE + CELLSIZE / 10,
                         CELLSIZE * 4 / 5,
                         CELLSIZE * 4 / 5)
        self.dirty = 1 

    def update(self):
        """ This is called by the view every frame. 
        If dirty, update the image based on the model.
        if self.dirty == 1, LayeredDirty.draw sets it to 0.  
        """
        
        # Reposition the rect to match the fruit's position.
        if self.dirty == 0:
            return

        
