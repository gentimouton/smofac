from constants import DIR_MAP, CELLSIZE
import pygame

class Cell(pygame.sprite.Sprite):
    
    def __init__(self, board, coords, pathdir, istrap):
        """ 
        coords are my coordinates.
        pathdir is the direction of the next cell in the path (e.g. DIR_UP).  
        """
        self.left, self.top = self.coords = coords
        self.board = board
        self.pathdir = pathdir # non-null for traps
        self.nextcell = None # will remain None for the exit
        self.prevcell = None # will remain None for the entrance
        self.fruit = None # TODO: temporary set by the board
        self.iswalkable = pathdir in DIR_MAP
        self.istrap = istrap
        
        cspr_left = self.left * CELLSIZE
        cspr_top = self.top * CELLSIZE
        self.rect = pygame.Rect(cspr_left, cspr_top, CELLSIZE, CELLSIZE)
        self.surf = pygame.Surface((CELLSIZE, CELLSIZE))
        
        if istrap:
            self.surf.fill((11, 11, 11))
        elif self.iswalkable:
            self.surf.fill((255, 255, 255))
        else:
            self.surf.fill((123, 123, 123))


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
        
    def trap(self):
        """ try to catch/drop/swap a fruit from/to/with the target cell.
        Return whether the trap has a fruit in the end.
        """
        myfruit = self.fruit
        targetfruit = self.target.fruit
        if myfruit:
            if targetfruit: # swap
                self.target.fruit = myfruit
                myfruit.cell = self.target
                self.fruit = targetfruit
                targetfruit.cell = self
                return True
            else: # release
                self.target.fruit = myfruit
                myfruit.cell = self.target
                self.fruit = None
                return False
        else: # I have no fruit
            if targetfruit: # catch
                self.fruit = targetfruit
                self.target.fruit = None
                targetfruit.cell = self
                return True
            else:
                return False
            