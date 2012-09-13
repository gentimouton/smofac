from constants import DIR_MAP, CELLSIZE, TRAP_COLOR, PATH_COLOR, BG_COLOR, \
    BLENDER_COLOR
from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame.surface import Surface
import logging

class Cell(Sprite):
    """ TODO: split into gfx and model parts. """
    
    def __init__(self, board, coords, pathdir, isentr=False, isjunc=False,
                 iswait=False, iskill=False, istrap=False):
        """ coords are my coordinates.
        pathdir is the direction of the next cell in the path (e.g. DIR_UP).  
        """
        self.coords = left, top = coords
        self.board = board
        self.pathdir = pathdir # non-null for traps
        self.nextcell = None # will remain None for the exit
        self.prevcell = None # will remain None for the entrance
        self.loadcell = None # will remain None for non-loading cells
        self.fruit = None # will be set by the board or cells
        self.iswalkable = pathdir in DIR_MAP # traps are walkable
        self.istrap = istrap
        self.load_dir = None
        
        #gfx
        cspr_left = left * CELLSIZE
        cspr_top = top * CELLSIZE
        self.rect = Rect(cspr_left, cspr_top, CELLSIZE, CELLSIZE)
        img = Surface((CELLSIZE, CELLSIZE))
        
        if istrap:
            img.fill(TRAP_COLOR)
        elif self.iswalkable: # but not a trap
            img.fill(PATH_COLOR)
        else:
            img.fill(BG_COLOR)
            
        self.image = img


    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        if self.fruit:
            fruitdata = 'FRUIT'
        else:
            fruitdata = 'NOFRUIT'
        return 'Cell: %s' % (str(self.coords)) + fruitdata
    
            
    @property
    def direction(self):
        """ Return the direction where the next cell is. """
        return self.pathdir
    
    def set_exitpath(self):
        """ The board found out that I am on the exit path. 
        Change my color. """
        self.image.fill(BLENDER_COLOR) 
        
    def set_waitingpath(self):
        """ The board found out I'm a cell in the waiting area. 
        Change my color. """
        self.image.fill(BLENDER_COLOR)
    
    def set_nonwalkable(self):
        """ The board found out there are more cells in the exit path
        than the longest recipe: some cells (like me) need to be removed """
        self.iswalkable = False
        self.image.fill(BG_COLOR)      
        
        
    #################### fruit stuff
      
    def empty(self):
        """ Remove my fruit """
        self.fruit = None
        
        
    def set_fruit(self, fruit, origin):
        """ Add a fruit to my cell. origin = cell of origin. """
        if self.fruit:
            logging.error('Trying to add fruit %s to cell %s,'\
                          + ' but it already has fruit %s'
                          % (fruit, self, self.fruit))
        # replace in any case
        self.fruit = fruit
        fruit.move_to(self)

    
    def progress_fruit(self, cell=None):
        """ Move my fruit to the next cell. 
        If a cell is specified, move it to that cell instead. 
        """
        myfruit = self.fruit
        if myfruit:
            target_cell = cell or self.nextcell
            target_cell.fruit = myfruit
            myfruit.move_to(target_cell)
            self.fruit = None
    
    def exit_fruit(self):
        """ Move a fruit to my exit cell. """
        myfruit = self.fruit
        if myfruit:
            loadcell = self.loadcell
            loadcell.fruit = myfruit
            myfruit.move_to(loadcell)
            self.fruit = None
    
    ################# trap stuff
    
        
    def set_target(self, targetcell):
        """ Called when the board wires the path. 
        When the cell is a trap, 
        its target is the cell it is stealing from. """
        self.target = targetcell
        
        
    def trap(self):
        """ try to catch/drop/swap a fruit from/to/with the target cell.
        Return whether the trap has a fruit in the end.
        """
        myfruit = self.fruit
        tcell = self.target
        tfruit = tcell.fruit
        
        if myfruit:# TODO: tricky for smooth mvt
            if tfruit: # swap 
                tcell.fruit = myfruit
                myfruit.release_to(tcell, swap=tfruit)
                self.fruit = tfruit
                tfruit.grab_to(self)
                caught = True
            else: # release
                tcell.fruit = myfruit
                myfruit.release_to(tcell)
                self.fruit = None
                caught = False
                
        else: # I have no fruit
            if tfruit: # catch
                self.fruit = tfruit
                tcell.fruit = None
                tfruit.grab_to(self)
                caught = True
            else:
                caught = False
        
        if caught:
            pass # TODO: make a sound
        else:
            pass # TODO: make another sound
