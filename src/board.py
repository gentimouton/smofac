from cell import Cell
from constants import BGCOLOR, RECIPES, FRUIT_LIST
from fruit import Fruit
import logging
import os
import pygame
import random



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
        
        self.E = self.get_cell(self.e_coords)
        self.J = self.get_cell(self.j_coords)
        self.W = self.get_cell(self.w_coords)
        self.X = self.get_cell(self.x_coords)
        self.K = self.get_cell(self.k_coords)
        self.T = self.get_cell(self.t_coords)
        
        # build the path: link cells to each other
        cell = self.E # entrance
        while not cell.nextcell: # ends when cells from entrance + loop areas are all linked  
            nextcoords = self.get_coords_from_direction(cell.coords, cell.pathdir)
            nextcell = self.get_cell(nextcoords)
            # wire
            cell.nextcell = nextcell
            nextcell.prevcell = cell
            # and keep going
            cell = nextcell

        cell = self.X
        while cell != self.K: 
            nextcoords = self.get_coords_from_direction(cell.coords, cell.pathdir)
            nextcell = self.get_cell(nextcoords)
            # wire
            cell.nextcell = nextcell
            nextcell.prevcell = cell
            # and keep going
            cell = nextcell

        self.rng = random.Random()
        self.rng.seed(0) # determinism = easier to debug
        self.spawn_timer = self.spawn_freq = 2 # spawn fruits every X frames 
        self.fruits = {}
        self.fruits_spawned = 0 # counter that ++ when a fruit appears
        

        ########### GFX ############
        
        # init the board display
        bg = pygame.Surface(screen.get_size())
        bg = bg.convert()
        bg.fill(BGCOLOR)
        for left in range(self.width):
            for top in range(self.height):
                cell = self.get_cell(left, top)
                bg.blit(cell.surf, cell.rect)
        
        self.bg = bg
        self.screen = screen
        screen.blit(bg, (0, 0))
        
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
        elif waypoint == 'X': # exit cell, just next to the waiting cell
            self.x_coords = coords
        elif waypoint == 'K': # kill cell at the end of the path 
            self.k_coords = coords
        elif waypoint == 'T': # trap
            self.t_coords = coords
            
        path_direction = cellstr[1]

        return Cell(self, coords, path_direction, waypoint=='T')
        
 
    
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
        if direction == 'U':
            c = left, top - 1
        elif direction == 'D':
            c = left, top + 1
        elif direction == 'L':
            c = left - 1, top
        elif direction == 'R':
            c = left + 1, top
        return c
    
    
    
    def update(self):
        """ move the fruits
        and blit the board and fruits on the screen 
        """
        self.screen.blit(self.bg, (0, 0))
        
        # exit cells
        kfruit = self.K.fruit
        if kfruit: # to the blender!
            del self.fruits[kfruit.fruit_id]
            self.K.fruit = None
        cell = self.K.prevcell
        while cell != None: # X.prevcell is None
            if cell.fruit:
                cell.nextcell.fruit = cell.fruit
                cell.fruit.cell = cell.nextcell
                cell.fruit = None
            cell = cell.prevcell

        # waiting cell
        wfruit = self.W.fruit
        if wfruit:
            if wfruit.isleaving: # part of a leaving recipe: kick it out!
                self.X.fruit = wfruit
                wfruit.cell = self.X
                self.W.fruit = None
                leftover_fruit = None
            else: # wfruit not part of a recipe already
                prev_fruit = self.W.prevcell.fruit
                if prev_fruit:
                    if (wfruit.fruit_type, prev_fruit.fruit_type) in RECIPES:
                        self.X.fruit = wfruit
                        wfruit.cell = self.X
                        self.W.fruit = None
                        prev_fruit.isleaving = True
                        leftover_fruit = None
                    else: # 2 fruits but no recipe matching
                        # wfruit keeps moving, 
                        # but we need to process the other fruits first
                        self.W.fruit = None
                        leftover_fruit = wfruit # stash wfruit
                else: # only 1 fruit: wait for another one
                    leftover_fruit = None
                    pass # TODO: fruit sprite should be "standing"
        else: # no fruit
            leftover_fruit = None

        # looping cells
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
            
        # entrance cells
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

        # spawn a fruit - must happen after all moves have been resolved        
        self.spawn()
                
        for fruit in self.fruits.values():
            fruit.update() # eventually move
            self.screen.blit(fruit.image, fruit.rect)

    def spawn(self):
        """ Spawn a fruit if it's time to do it. """
        
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            if self.E.fruit:
                logging.info('game over') # TODO: stop the game
            else:
                fruit_id = self.fruits_spawned
                random_int = self.rng.randint(0, len(FRUIT_LIST) - 1)
                fruit_type = FRUIT_LIST[random_int]
                fruit = Fruit(self.E, fruit_type, fruit_id) # strawberry
                self.fruits[fruit_id] = fruit
                self.E.fruit = fruit
                self.spawn_timer = self.spawn_freq
                self.fruits_spawned += 1

        
        
