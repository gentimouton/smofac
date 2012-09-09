from constants import DIR_MAP, CELLSIZE
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
            self.image.fill((11, 11, 11))
        elif self.iswalkable:
            self.image.fill((255, 255, 255))
        else:
            self.image.fill((123, 123, 123))


    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        if self.fruit:
            fruitdata = 'FRUIT'
        else:
            fruitdata = 'NOFRUIT'
        return 'Cell: %s' % (str(self.coords)) + fruitdata

    def set_target(self, targetcell):
        """ When the cell is a trap, 
        its target is the cell it is stealing from. """
        self.target = targetcell
        
        
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
        fruit.move_to(self.coords)

    
    def progress_fruit(self, cell=None):
        """ Move my fruit to the next cell. 
        If a cell is specified, move it to that cell instead. 
        TODO: interpolate pos of fruit spr between target_cell and self.
        """
        myfruit = self.fruit
        if myfruit:
            target_cell = cell or self.nextcell
            target_cell.fruit = myfruit
            myfruit.move_to(target_cell.coords)
            self.fruit = None
    
            
    def trap(self):
        """ try to catch/drop/swap a fruit from/to/with the target cell.
        Return whether the trap has a fruit in the end.
        """
        myfruit = self.fruit
        tcell = self.target
        targetfruit = tcell.fruit
        if myfruit:
            if targetfruit: # swap
                tcell.fruit = myfruit
                myfruit.move_to(tcell.coords)
                self.fruit = targetfruit
                targetfruit.move_to(self.coords)
                caught = True
            else: # release
                tcell.fruit = myfruit
                myfruit.move_to(tcell.coords)
                self.fruit = None
                caught = False
        else: # I have no fruit
            if targetfruit: # catch
                self.fruit = targetfruit
                tcell.fruit = None
                targetfruit.move_to(self.coords)
                caught = True
            else:
                caught = False
        
        if caught:
            pass # TODO: make a sound
        else:
            pass # TODO: make another sound
