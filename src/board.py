import logging
import os
import pygame

# constants
DIR_UP = 1
DIR_DOWN = 2
DIR_LEFT = 3
DIR_RIGHT = 4
DIR_MAP = {'U': DIR_UP,
           'D': DIR_DOWN,
           'L': DIR_LEFT,
           'R': DIR_RIGHT,
           '.': None
           }

class Board():
    
    def __init__(self, filename, screen):
        """ filename of the map, 
        screen to blit on
        """
        
        self.filename = filename
        
        fullname = os.path.join(os.pardir, 'boards', filename)        
        try:    
            f = open(fullname)
        except IOError:
            logging.error('Board %s not found at %s' % filename, fullname)
            
        lines = f.readlines() #might be optimized: for line in open("file.txt"):
        self.__cellgrid = [] #contains game board
        self.worldrepr = '' # string visually representing the world map
        
        # sanity checks on board width and height
        self.height = len(lines)
        if self.height == 0:
            logging.error('Board %s has no lines.' % filename)
        else:
            self.width = len(lines[0].strip().split(','))
            if self.width == 0:
                logging.error('The first row of board %s has no cells.' % filename)
        
        # build the cell matrix
        for i in range(self.height):
            tmprow = []
            line = lines[i].strip().split(',')
            self.worldrepr = self.worldrepr + lines[i]
            
            for j in range(len(line)):
                coords = j, i # __cellgrid[i][j] = i from top, j from left
                cell = self.build_cell(coords, line[j])
                tmprow.append(cell)

            self.__cellgrid.append(tmprow)
        
        # build the path: link cells to each other
        cell = self.get_cell(self.e_coords) # entrance
        while not cell.nextcell: # ends when cells from the entrance + loop areas are all linked  
            nextcoords = self.get_coords_from_direction(cell.coords, cell.pathdir)
            nextcell = self.get_cell(nextcoords)
            # wire
            cell.nextcell = nextcell
            nextcell.prevcell = cell
            # and keep going
            cell = nextcell
        
        self.E = self.get_cell(self.e_coords)
        self.J = self.get_cell(self.j_coords)
        self.W = self.get_cell(self.w_coords)
        self.X = self.get_cell(self.x_coords)
        self.K = self.get_cell(self.k_coords)
        
        # TODO: temporary spawn 1 fruit
        fruit = Fruit(self.E)
        self.fruits = [fruit]
        self.E.fruit = fruit
        
        
        ########### GFX ############
        
        # init the board display
        bg = pygame.Surface(screen.get_size())
        bg = bg.convert()
        bg.fill((33, 33, 33))
        celsize = 50
        for left in range(self.width):
            for top in range(self.height):
                cspr_left = left * celsize
                cspr_top = top * celsize
                cellrect = pygame.Rect(cspr_left, cspr_top, celsize, celsize)
                cellsurf = pygame.Surface((celsize, celsize))
                # blit the cell to world bg
                if self.get_cell(left, top).iswalkable():
                    cellsurf.fill((255, 255, 255))
                else:
                    cellsurf.fill((123, 123, 123))
                bg.blit(cellsurf, cellrect)
        
        self.bg = bg
        self.screen = screen
        screen.blit(bg, (0, 0))
        for fruit in self.fruits:
            self.screen.blit(fruit.image, fruit.rect)        
        
        logging.info('Board built')
        
        

    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return '%s, %d x %d' % (self.filename, self.width, self.height) \
            + '\n' + self.worldrepr
            


    def build_cell(self, coords, cellstr):                
        """ Each cell is stored as XY in the map file, 
        with X being the type of cell (- for walkable, E for entrance),
        and Y being the direction to go next in the path (U,D,L,R).
        """
        waypoint = cellstr[0]
        if waypoint == 'E': # entrance cell
            self.e_coords = coords
        elif waypoint == 'J': # junction cell
            self.j_coords = coords
        elif waypoint == 'W': # waiting cell
            self.w_coords = coords
        elif waypoint == 'X': # exit cell, below waiting cell
            self.x_coords = coords
        elif waypoint == 'K': # kill cell 
            self.k_coords = coords

        if waypoint == 'W':
            path_direction = DIR_MAP[cellstr[1]]
            #exit_direction = DIR_MAP[cellstr[2]] # TODO: add exit path
        else:
            path_direction = DIR_MAP[cellstr[1]]

        return Cell(self, coords, path_direction)
        
 
    
    def get_cell(self, lefttop, top=None):
        """ Get a cell from its coords.
        Accepts get_cell(left,top) or get_cell( (left,top) ).
        Returns None if out of map.        
        """ 
        try:
            if top is not None: #top is specified ('is not None' because top can be 0)
                left = lefttop
                if left < 0 or top < 0: # outside of the map
                    return None
                else:
                    return self.__cellgrid[top][left]
            else: #top was not specified
                left, top = lefttop
                if left < 0 or top < 0:# outside of the map
                    return None
                else:
                    return self.__cellgrid[top][left]
        except IndexError: #outside of the map
            return None
        
        
    def get_coords_from_direction(self, coords, direction):
        """ If given coords = i,j,
        and direction = DIR_UP,
        then return i, j-1
        """
        left, top = coords
        if direction == DIR_UP:
            c = left, top - 1
        elif direction == DIR_DOWN:
            c = left, top + 1
        elif direction == DIR_LEFT:
            c = left - 1, top
        elif direction == DIR_RIGHT:
            c = left + 1, top
        return c
    
    
    
    def update(self):
        """ move the fruits
        and blit the board and fruits on the screen 
        """
        self.screen.blit(self.bg, (0, 0))
        
        # loading cell
        if self.W.fruit:
            leftover_fruit = self.W.fruit
            self.W.fruit = None
        else:
            leftover_fruit = None
            
        # looping area
        cell = self.W.prevcell
        while cell != self.W:
            if cell.fruit:
                cell.nextcell.fruit = cell.fruit
                cell.fruit.cell = cell.nextcell
                cell.fruit = None
            cell = cell.prevcell
        
        if leftover_fruit:
            self.W.nextcell.fruit = leftover_fruit
            leftover_fruit.cell = self.W.nextcell
            
        # entrance area
        if self.J.fruit:
            if self.J.nextcell.fruit:
                pass # TODO: sprite should be "standing" instead of "walking"
            else: # join the loop
                self.J.nextcell.fruit = self.J.fruit
                self.J.fruit.cell = self.J.nextcell
                self.J.fruit = None
        cell = self.J.prevcell
        while cell != None: # None = E.prevcell
            if cell.fruit:
                if cell.nextcell.fruit:
                    pass # TODO: "standing" sprite 
                else: # no fruit ahead: move
                    cell.nextcell.fruit = cell.fruit
                    cell.fruit.cell = cell.nextcell
                    cell.fruit = None
            cell = cell.prevcell
        
        for fruit in self.fruits:
            fruit.update() # eventually move
            self.screen.blit(fruit.image, fruit.rect) 
            
        
##########################################################################

class Fruit(pygame.sprite.Sprite):
    
    def __init__(self, cell):
        self.cell = cell
        self.update()
        self.image = pygame.Surface((50, 50))
        self.image.fill((111, 0, 0))
    
    def __repr__(self):
        return 'Fruit at %s' % (str(self.cell.coords))
    def __str__(self):
        return self.__repr__()
        

    def update(self):
        left, top = self.cell.coords
        self.rect = pygame.Rect(left * 50, top * 50, 50, 50)
        
        
        
class Cell():
    
    def __init__(self, board, coords, pathdir):
        """ 
        coords are my coordinates.
        pathdir is the direction of the next cell in the path (e.g. DIR_UP).  
        """
        self.left, self.top = self.coords = coords
        self.board = board
        self.pathdir = pathdir
        self.nextcell = None # will remain None for the exit
        self.prevcell = None # will remain None for the entrance
        self.fruit = None # TODO: temporary set by the board
        
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        if self.fruit:
            fruitdata = 'FRUIT'
        else:
            fruitdata = 'NOFRUIT'
        return 'Cell: %s' % (str(self.coords)) + fruitdata
  
    def iswalkable(self):
        return self.prevcell or self.nextcell
