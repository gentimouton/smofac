from constants import DIR_MAP, CELLSIZE, TRAP_COLOR, PATH_COLOR, BG_COLOR
import logging
import pygame

class Cell(pygame.sprite.Sprite):
    
    def __init__(self, board, coords, pathdir, isentr=False, isjunc=False,
                 iswait=False, isexit=False, iskill=False, istrap=False):
        """ coords are my coordinates.
        pathdir is the direction of the next cell in the path (e.g. DIR_UP).  
        """
        self.left, self.top = self.coords = coords
        self.board = board
        self.pathdir = pathdir # non-null for traps
        self.nextcell = None # will remain None for the exit
        self.prevcell = None # will remain None for the entrance
        self.fruit = None # will be set by the board or cells
        self.iswalkable = pathdir in DIR_MAP
        self.istrap = istrap
        
        cspr_left = self.left * CELLSIZE
        cspr_top = self.top * CELLSIZE
        self.rect = pygame.Rect(cspr_left, cspr_top, CELLSIZE, CELLSIZE)
        self.image = pygame.Surface((CELLSIZE, CELLSIZE))
        
        if istrap:
            self.image.fill(TRAP_COLOR)
        elif self.iswalkable:
            self.image.fill(PATH_COLOR)
        else:
            self.image.fill(BG_COLOR)


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
    
    #################### fruit stuff
      
    def empty(self):
        """ Remove my fruit """
        self.fruit = None
        
        
    def set_fruit(self, fruit, origin):
        """ Add a fruit to my cell. origin = cell of origin. 
        TODO: interpolate pos of fruit spr between self and origin.
        """
        if self.fruit:
            logging.error('Trying to add fruit %s to cell %s,'\
                          + ' but it already has fruit %s'
                          % (fruit, self, self.fruit))
        # replace in any case
        self.fruit = fruit
        fruit.move_to(self) # TODO: tricky for smooth fruit mvt

    
    def progress_fruit(self, cell=None):
        """ Move my fruit to the next cell. 
        If a cell is specified, move it to that cell instead. 
        TODO: interpolate pos of fruit spr between target_cell and self.
        """
        myfruit = self.fruit
        if myfruit:
            target_cell = cell or self.nextcell
            target_cell.fruit = myfruit
            myfruit.move_to(target_cell)
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
                myfruit.release(tcell)
                self.fruit = tfruit
                tfruit.grab(self)
                caught = True
            else: # release
                tcell.fruit = myfruit
                myfruit.release(tcell)
                self.fruit = None
                caught = False
                
        else: # I have no fruit
            if tfruit: # catch
                self.fruit = tfruit
                tcell.fruit = None
                tfruit.grab(self)
                caught = True
            else:
                caught = False
        
        if caught:
            pass # TODO: make a sound
        else:
            pass # TODO: make another sound
