from cell import Cell
from constants import RECIPES, DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
from events import BoardBuiltEvent, TickEvent, BoardUpdatedEvent, \
    PRIO_TICK_MODEL, RecipeMatchEvent
from input import TriggerTrapEvent
from spawner import Spawner
import logging
import os


        
class Board():
    
    def __init__(self, game, em, mapname):
        """ Build the board. """
        
        self.mapname = mapname
        self.game = game
        
        loaded_map = self._load_mapfile(mapname)
        self.height, self.width, self._cellgrid = loaded_map[0:3]
        self.E, self.J, self.W, self.X, self.K, self.T = loaded_map[3:] 
        
        self._build_path()
        self.fruits = {}
        
        self.spawner = Spawner(em, self.E)

        self._em = em
        em.subscribe(TriggerTrapEvent, self.on_triggertrap)
        em.subscribe(TickEvent, self.on_tick, PRIO_TICK_MODEL)
        
        # notify that the board is built
        logging.info('Board built')
        ev = BoardBuiltEvent(self.width, self.height, self)
        em.publish(ev)
        
        

    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return '%s, %d x %d' % (self.filename, self.width, self.height)
            



    def _load_mapfile(self, filename):
        """ Return the height, width, and lines from the map file. 
        Also do some sanity checking on the way.
        This method is the only one concerned with the map file format.
        Each cell is stored as XY in the map file, 
        with X being the type of cell (- for walkable, E for entrance),
        and Y being the direction to go next in the path (U,D,L,R).
        """
        
        # open file
        filepath = os.path.join(os.pardir, 'boards', filename)
        try:    
            f = open(filepath)
        except IOError:
            logging.error('Board %s not found at %s' % (filename, filepath))
        lines = f.readlines()

        # sanity checks on board width and height
        height = len(lines)
        if height == 0:
            logging.critical('Board %s has no lines.' % filename)
            exit()
        else:
            width = len(lines[0].strip().split(','))
            if width <= 1:
                logging.critical('Board %s has not enough cells.' % filename)
                exit()
        
        # build the cell matrix
        cellgrid = []
        entr_cell = junc_cell = wait_cell = None
        exit_cell = kill_cell = trap_cell = None  
        for i in range(height):
            tmprow = []
            line = lines[i].strip().split(',')
            for j in range(len(line)):
                coords = j, i # _cellgrid[i][j] = i from top, j from left
                waypoint, path_direction = line[j][0], line[j][1]
                if waypoint == 'E':
                    cell = Cell(self, coords, path_direction, isentr=True)
                    entr_cell = cell
                elif waypoint == 'J':
                    cell = Cell(self, coords, path_direction, isjunc=True)
                    junc_cell = cell
                elif waypoint == 'W':
                    cell = Cell(self, coords, path_direction, iswait=True)
                    wait_cell = cell
                elif waypoint == 'X':
                    cell = Cell(self, coords, path_direction, isexit=True)
                    exit_cell = cell
                elif waypoint == 'K':
                    cell = Cell(self, coords, path_direction, iskill=True)
                    kill_cell = cell
                elif waypoint == 'T':
                    cell = Cell(self, coords, path_direction, istrap=True)
                    trap_cell = cell
                else:
                    cell = Cell(self, coords, path_direction)
                                        
                tmprow.append(cell)

            cellgrid.append(tmprow)
        
        # check there's at least one of each cell
        if not entr_cell or not junc_cell or not wait_cell\
            or not exit_cell or not kill_cell or not trap_cell:
            logging.critical('Board %s is missing waypoints' % filename)

        return (height, width, cellgrid,
                entr_cell, junc_cell, wait_cell,
                exit_cell, kill_cell, trap_cell)
        

    
    def _build_path(self):
        """ build the path: link cells to each other """
        
        # entrance and loop areas
        cell = self.E 
        while not cell.nextcell: # ends when the loop is linked  
            nextcoords = self._get_coords_from_dir(cell.coords, cell.pathdir)
            nextcell = self.get_cell(nextcoords)
            # wire
            cell.nextcell = nextcell
            nextcell.prevcell = cell
            # and keep going
            cell = nextcell

        # exit area
        cell = self.X
        while cell != self.K: 
            nextcoords = self._get_coords_from_dir(cell.coords, cell.pathdir)
            nextcell = self.get_cell(nextcoords)
            # wire
            cell.nextcell = nextcell
            nextcell.prevcell = cell
            # and keep going
            cell = nextcell

        # wire the trap
        target_coords = self._get_coords_from_dir(self.T.coords, self.T.pathdir)
        target_cell = self.get_cell(target_coords)
        self.T.set_target(target_cell)        

    
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
                    return self._cellgrid[top][left]
            else: #top was not specified
                left, top = lefttop
                if left < 0 or top < 0:# outside of the map
                    return None
                else:
                    return self._cellgrid[top][left]
        except IndexError: #outside of the map
            return None
        
        
    def _get_coords_from_dir(self, coords, direction):
        """ If given coords = i,j, and direction = DIR_UP,
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
    
    
    
    def on_tick(self, tickevt):
        """ move the fruits """
        
        # blender/kill cell
        kfruit = self.K.fruit
        if kfruit: # to the blender!
            del self.fruits[kfruit.fruit_id]
            logging.debug('removed fruit#%d - %s, now have fruits %s' 
                         % (kfruit.fruit_id, kfruit.fruit_type,
                            ','.join([str(k) for k in self.fruits.keys()])))
            self.K.fruit = None
        # exit cells
        cell = self.K.prevcell
        while cell != None: # X.prevcell is None
            if cell.fruit:
                cell.nextcell.fruit = cell.fruit
                cell.fruit.cell = cell.nextcell
                cell.fruit = None
            cell = cell.prevcell

        # waiting cell. The stashed fruit is used to allow 
        # a full loop area to still be able to move.
        wfruit = self.W.fruit
        if wfruit:
            if wfruit.isleaving: # part of a leaving recipe: kick it out!
                self.X.fruit = wfruit
                wfruit.cell = self.X
                self.W.fruit = None
                stashed_fruit = None
            else: # wfruit not part of a recipe already
                prev_fruit = self.W.prevcell.fruit
                if prev_fruit:
                    fruit_list = (wfruit.fruit_type, prev_fruit.fruit_type)
                    ismatch = self.game.recipe_match(fruit_list)
                    if ismatch:
                        logging.debug('Recipe match from fruits %d and %d'
                                     % (wfruit.fruit_id, prev_fruit.fruit_id))
                        self.X.fruit = wfruit
                        wfruit.cell = self.X
                        self.W.fruit = None
                        prev_fruit.isleaving = True
                        stashed_fruit = None
                    else: # 2 fruits but no recipe matching
                        # wfruit keeps moving, 
                        # but we need to process the other fruits first
                        self.W.fruit = None
                        stashed_fruit = wfruit # stash wfruit
                else: # only 1 fruit: wait for another one
                    stashed_fruit = None
                    pass # TODO: fruit sprite should be "standing"
        else: # no fruit
            stashed_fruit = None

        # looping cells
        cell = self.W.prevcell
        while cell != self.W:
            if cell.fruit:
                cell.nextcell.fruit = cell.fruit
                cell.fruit.cell = cell.nextcell
                cell.fruit = None
            cell = cell.prevcell
        
        if stashed_fruit:
            self.W.nextcell.fruit = stashed_fruit
            stashed_fruit.cell = self.W.nextcell
            
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

        # tick the fruit spawner - must happen after all moves have been resolved        
        spawned, fruit = self.spawner.tick(tickevt.loopduration)
        if spawned:
            if fruit:
                self.fruits[fruit.fruit_id] = fruit # TODO: this is disgusting!
            else:
                logging.info('game over') # TODO: QuitEvent
        
        for fruit in self.fruits.values():
            fruit.update() # eventually move
        
        ev = BoardUpdatedEvent(self.fruits.values())
        self._em.publish(ev)




    def on_triggertrap(self, inputevt):
        """ User pushed the trap key. Try to trap a fruit. """
        caught = self.T.trap()
        
        
