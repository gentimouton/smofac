from constants import FRUIT_COLORS, FONT_SIZE, CELLSIZE, FRUIT_SPEED, DIR_UP, \
    DIR_DOWN, DIR_LEFT, DIR_RIGHT, STEPS_PER_CELL
from pygame.font import Font
from pygame.rect import Rect
from pygame.sprite import DirtySprite
from pygame.surface import Surface
from pygame.transform import rotate


class FruitSpr(DirtySprite):
    """ Representation on the screen of a fruit. """
    
    def __init__(self, fruit, interp_step):
        """ Prepare the fruit's spr: a square diamond 
        with a number in the center.
        interp_step determines where to position the sprite, 
        based on the view's current sprite step. 
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
        self.resync(interp_step)
        
        self.image = img
        
    
    def __repr__(self):
        return '%d at %s' % (self.fruit, str(self.rect))
    def __str__(self):
        return self.__repr__()
        
    
    def resync(self, interp_step):
        """ synchronize the spr coords with the model coords,
        and shift the spr based on the current step of interpolation. 
        """
        fruit = self.fruit

        # compute the speed vector
        spd_x = spd_y = 0 # speed vector: how many px to move per step
        if interp_step <= STEPS_PER_CELL / 2:
            # 1st half of interpolation: join my prev cell and current cell
            cell = fruit.prevcell
        else:# 2nd half: join current cell and next cell
            cell = fruit.cell
        if cell.direction == DIR_UP: # the spr should move up
            spd_y = -CELLSIZE / STEPS_PER_CELL
        elif cell.direction == DIR_DOWN:
            spd_y = CELLSIZE / STEPS_PER_CELL
        elif cell.direction == DIR_LEFT:
            spd_x = -CELLSIZE / STEPS_PER_CELL
        elif cell.direction == DIR_RIGHT:
            spd_x = CELLSIZE / STEPS_PER_CELL
        
        # offset the first step of the spr such that at mid-model-tick,
        # the spr will be right in the middle of cell
        offset_x = (int(STEPS_PER_CELL / 2) - interp_step) * spd_x
        offset_y = (int(STEPS_PER_CELL / 2) - interp_step) * spd_y
        left = fruit.coords[0] * CELLSIZE - offset_x 
        top = fruit.coords[1] * CELLSIZE - offset_y 
        
        self.rect = Rect(left, top, CELLSIZE, CELLSIZE)
        self.dirty = 1 
        # dirty is set to 0 by the LayeredDirty sprite group it belongs to.        
        

    def update(self, duration):
        """ Eventually update the fruit sprite position. 
        This is called by the view every frame.
        If dirty, LayeredDirty.draw sets it to 0.  
        """
        return # nothing to do

