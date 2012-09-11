from constants import FRUIT_COLORS, FONT_SIZE, CELLSIZE, FRUIT_SPEED, DIR_UP, \
    DIR_DOWN, DIR_LEFT, DIR_RIGHT
from pygame.font import Font
from pygame.rect import Rect
from pygame.sprite import DirtySprite
from pygame.surface import Surface


LOOPING = 'looping' # in the board loop
LEAVING = 'leaving' # on (or scheduled for) the exit path, 
WAITING = 'waiting' # standing still


class Fruit(DirtySprite):
    
    def __init__(self, cell, fruit_type, fruit_num):
        self.fruit_type = fruit_type # 'S' for strawberry
        self.fruit_num = fruit_num
        self.loop()
        
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
        
        # fruit's model position
        self.move_to(cell)
        
        
    
    def __repr__(self):
        return '%s#%d %s' % (self.fruit_type, self.fruit_num, self.state)
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
    @property
    def is_looping(self):
        return self.state == LOOPING
    def loop(self):
        self.state = LOOPING
    
    
    def grab(self, cell):
        """ When the fruit is captured, it becomes waiting. """
        self.wait()
        self.move_to(cell)
        
    def release(self, cell):
        self.loop()
        self.move_to(cell)
        
        
    def move_to(self, cell):
        """ Move the fruit to a cell. 
        We need to know the next cell for appropriate positioning.
        """

        # compute the fruit's rect center coords
        # and the sprite speed vector
        ctr_left = cell.coords[0] * CELLSIZE
        ctr_top = cell.coords[1] * CELLSIZE
        if cell.direction == DIR_UP: # the spr should move up
            ctr_left += CELLSIZE / 2
            ctr_top += CELLSIZE
            spr_dx, spr_dy = 0, -CELLSIZE / 4
        elif cell.direction == DIR_DOWN:
            ctr_left += CELLSIZE / 2
            spr_dx, spr_dy = 0, CELLSIZE / 4
        elif cell.direction == DIR_LEFT:
            ctr_top += CELLSIZE / 2
            spr_dx, spr_dy = -CELLSIZE / 4, 0
        elif cell.direction == DIR_RIGHT:
            ctr_left += CELLSIZE
            ctr_top += CELLSIZE / 2
            spr_dx, spr_dy = CELLSIZE / 4, 0
        self.rect = Rect(0, 0, CELLSIZE * 4 / 5, CELLSIZE * 4 / 5)
        self.rect.center = ctr_left, ctr_top
        
        self.spr_delta = spr_dx, spr_dy
        self.spr_timer = FRUIT_SPEED / 4 # when to update the sprite's position
        
        self.dirty = 1 


    def update(self, duration):
        """ Eventually update the fruit sprite position. 
        This is called by the view every frame.
        If dirty, LayeredDirty.draw sets it to 0.  
        """
        
        if not self.is_looping:
            return # only need to update the sprite of moving fruits
         
        self.spr_timer -= duration
        if self.spr_timer <= 0: # time to move the spr  
            dx, dy = self.spr_delta
            self.rect.move_ip(dx, dy)
            self.spr_timer = FRUIT_SPEED / 4
            self.dirty = 1
            
