from board import DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
from config import cell_size, font_size, steps_per_cell
from constants import FRUIT_COLORS
from pygame.font import Font
from pygame.rect import Rect
from pygame.sprite import DirtySprite
from pygame.surface import Surface
from pygame.transform import rotate


class FruitSpr(DirtySprite):
    """ Representation on the screen of a fruit. """
    
    def __repr__(self):
        return '%d at %s' % (self.fruit.fruit_num, str(self.rect))
    def __str__(self):
        return self.__repr__()
    
    
    def __init__(self, fruit, interp_step):
        """ Prepare the fruit's spr: a square diamond 
        with a number in the center.
        interp_step determines where to position the sprite, 
        based on the view's current sprite step. 
        """
        DirtySprite.__init__(self)
        self.fruit = fruit
        
        # make the square
        sq_surf = Surface((cell_size / 1.414, cell_size / 1.414))
        sq_surf.set_colorkey((255, 0, 255))  # magenta = color key
        sq_surf.fill(FRUIT_COLORS[fruit.fruit_type])
        # rotate for a diamond
        dm_surf = rotate(sq_surf, 45)
        blit_rect = Rect(0, 0, cell_size * 1.414, cell_size * 1.414)
        # blit the diamond as the fruit's image
        img = Surface((cell_size, cell_size))
        img.set_colorkey((255, 0, 255))  # magenta = color key
        img.fill((255, 0, 255))
        img.blit(dm_surf, blit_rect)
        
        # add text at the center
        self.font = Font(None, font_size) 
        txtsurf = self.font.render(str(fruit.fruit_num), True, (0, 0, 0))
        textpos = txtsurf.get_rect(center=(cell_size / 2, cell_size / 2))
        img.blit(txtsurf, textpos)
        
        # prepare rect to blit on screen
        self.resync(interp_step)
        
        self.image = img
        
        
    
    def resync(self, interp_step):
        """ synchronize the spr coords with the model coords,
        and shift the spr based on the current step of interpolation. 
        """
        fruit = self.fruit
        
        if fruit.is_waiting:
            cell = fruit.cell
            left = cell.coords[0] * cell_size
            top = cell.coords[1] * cell_size
            
        else: # looping or leaving
            # compute the speed vector
            spd_x = spd_y = 0 # speed vector: how many px to move per step
            if interp_step <= steps_per_cell / 2:
                # 1st half of interpolation: join my prev cell and current cell
                pcell = fruit.prevcell
                if fruit.is_leaving:
                    direction = pcell.load_dir or pcell.direction
                else: # looping
                    direction = pcell.direction
            else:# 2nd half: join current cell and next cell
                cell = fruit.cell
                if fruit.is_leaving:
                    direction = cell.load_dir or cell.direction
                else: # looping
                    direction = fruit.cell.direction
                
            if direction == DIR_UP: # the spr should move up
                spd_y = -cell_size / steps_per_cell
            elif direction == DIR_DOWN:
                spd_y = cell_size / steps_per_cell
            elif direction == DIR_LEFT:
                spd_x = -cell_size / steps_per_cell
            elif direction == DIR_RIGHT:
                spd_x = cell_size / steps_per_cell
            
            # offset the first step of the spr such that at mid-model-tick,
            # the spr will be right in the middle of cell
            offset_x = (int(steps_per_cell / 2) - interp_step) * spd_x
            offset_y = (int(steps_per_cell / 2) - interp_step) * spd_y
            left = fruit.coords[0] * cell_size - offset_x 
            top = fruit.coords[1] * cell_size - offset_y 
        
        self.rect = Rect(left, top, cell_size, cell_size)
        self.dirty = 1 
        # dirty is set to 0 by the LayeredDirty sprite group it belongs to.        
        

    def update(self, duration):
        """ Eventually update the fruit sprite position. 
        This is called by the view every frame.
        If dirty, LayeredDirty.draw sets it to 0.  
        """
        return # nothing to do

