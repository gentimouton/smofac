from constants import FRUIT_COLORS, FONT_SIZE, CELLSIZE, FRUIT_SPEED, DIR_UP, \
    DIR_DOWN, DIR_LEFT, DIR_RIGHT
from pygame.font import Font
from pygame.rect import Rect
from pygame.sprite import DirtySprite
from pygame.surface import Surface
from pygame.transform import rotate


class FruitSpr(DirtySprite):
    """ Representation on the screen of a fruit. """
    
    def __init__(self, fruit):
        """ Prepare the fruit's spr: a square diamond 
        with a number in the center.
        """
        DirtySprite.__init__(self)
        self.fruit = fruit
        
        # make the square
        sq_surf = Surface((CELLSIZE / 1.414, CELLSIZE / 1.414))
        sq_surf.set_colorkey((255, 0, 255))  # magenta = color key
        sq_surf.fill(FRUIT_COLORS[fruit.fruit_type])
        # rotate for a diamond
        dm_surf = rotate(sq_surf, 45)
        blit_rect = Rect(0, 0, CELLSIZE * 1.414, CELLSIZE * 1.414)
        # blit the diamond as the fruit's image
        img = Surface((CELLSIZE, CELLSIZE))
        img.set_colorkey((255, 0, 255))  # magenta = color key
        img.fill((255, 0, 255))
        img.blit(dm_surf, blit_rect)
        
        # add text at the center
        self.font = Font(None, FONT_SIZE) 
        txtsurf = self.font.render(str(fruit.fruit_num), True, (0, 0, 0))
        textpos = txtsurf.get_rect(center=(CELLSIZE / 2, CELLSIZE / 2))
        img.blit(txtsurf, textpos)
        
        # prepare rect to blit on screen
        left = fruit.coords[0] * CELLSIZE
        top = fruit.coords[1] * CELLSIZE
        self.rect = Rect(left, top, CELLSIZE, CELLSIZE) 
        
        self.dirty = 1 # when 1, the view will blit it. 
        # dirty is set to 0 by the LayeredDirty sprite group it belongs to.
 
        self.image = img
        
    
    def __repr__(self):
        return '%d at %s' % (self.fruit, str(self.rect))
    def __str__(self):
        return self.__repr__()
        
    
    def resync(self):
        """ synchronize the spr coords with the model coords """
        fruit = self.fruit
        left = fruit.coords[0] * CELLSIZE
        top = fruit.coords[1] * CELLSIZE
        self.rect = Rect(left, top, CELLSIZE, CELLSIZE)         
        self.dirty = 1 

    
#    def move_to(self, cell, in_trap=False):
#        """ Move the fruit to a cell. 
#        We need to know the next cell for appropriate positioning.
#        """
#
#        if in_trap: # fruit just got grabbed
#            self.wait()
#            
#            #gfx
#            left = cell.coords[0] * CELLSIZE
#            top = cell.coords[1] * CELLSIZE
#            self.rect.topleft = (left + CELLSIZE / 10, top + CELLSIZE / 10)
#            self.spr_delta = 0, 0 # dont move the spr
#            self.spr_timer = 0 # TODO: replace by the swapped fruit's timer
#            # TODO: what is the timer if no fruit to swap with? 
#        
#        else: # waiting or looping
#            #gfx
#            ctr_left = cell.coords[0] * CELLSIZE
#            ctr_top = cell.coords[1] * CELLSIZE
#            if cell.direction == DIR_UP: # the spr should move up
#                ctr_left += CELLSIZE / 2
#                ctr_top += CELLSIZE
#                spr_dx, spr_dy = 0, -CELLSIZE / 2 # the sprite speed vector
#            elif cell.direction == DIR_DOWN:
#                ctr_left += CELLSIZE / 2
#                spr_dx, spr_dy = 0, CELLSIZE / 2
#            elif cell.direction == DIR_LEFT:
#                ctr_top += CELLSIZE / 2
#                spr_dx, spr_dy = -CELLSIZE / 2, 0
#            elif cell.direction == DIR_RIGHT:
#                ctr_left += CELLSIZE
#                ctr_top += CELLSIZE / 2
#                spr_dx, spr_dy = CELLSIZE / 2, 0
#            # center the spr rect
#            self.rect.center = ctr_left, ctr_top
#            
#            # when and how to update the sprite's position
#            self.spr_delta = spr_dx, spr_dy
#            self.spr_timer = 1000 * FRUIT_SPEED / 2 
#        
#        self.dirty = 1 


    def update(self, duration):
        """ Eventually update the fruit sprite position. 
        This is called by the view every frame.
        If dirty, LayeredDirty.draw sets it to 0.  
        """
        return # nothing to do
        
#        if not self.is_looping:
#            return # only need to update the sprite of moving fruits
#         
#        self.spr_timer -= duration
#        if self.spr_timer <= 0: # time to move the spr  
#            dx, dy = self.spr_delta
#            self.rect.move_ip(dx, dy)
#            self.spr_timer = 1000 * FRUIT_SPEED / 2
#            self.dirty = 1
#            

