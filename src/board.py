from cell import Cell
from constants import DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT, FRUIT_SPEED
from events import BoardBuiltEvent, TickEvent, BoardUpdatedEvent, \
    PRIO_TICK_MODEL, FruitKilledEvent, AccelerateFruitsEvent, DecelerateFruitsEvent, \
    FruitSpeedEvent
from input import TriggerTrapEvent
from spawner import Spawner
import logging
import os


        
class Board():
    
    def __init__(self, game, em, mapname, waitzone_length):
        """ Build the board. """
        
        self.mapname = mapname
        self.game = game
        
        # build the map
        loaded_map = self._load_mapfile(mapname)
        self.height, self.width, self._cellgrid = loaded_map[0:3]
        self.E, self.J, self.W, self.K, self.T = loaded_map[3:8] 
        load_cells_count = loaded_map[8] # number of cells in loading zone
        if load_cells_count < waitzone_length:
            logging.warn('Longest recipe has %d fruits,' % waitzone_length
                         + ' but the map has only %d loading cells' 
                         % load_cells_count)
        self.waitzone_length = waitzone_length
        
        self._build_path(waitzone_length)
        
        self.fruits = set()
        self.fruit_speed = FRUIT_SPEED # in cells per second
        self.fruit_mvt_timer = 1000. / self.fruit_speed # decreased each clock tick 
        # When it reaches zero or below, move the fruits.
        self.spawner = Spawner(em, self.E)

        self._em = em
        em.subscribe(TriggerTrapEvent, self.on_triggertrap)
        em.subscribe(TickEvent, self.on_tick, PRIO_TICK_MODEL)
        em.subscribe(AccelerateFruitsEvent, self.on_faster_fruits)
        em.subscribe(DecelerateFruitsEvent, self.on_slower_fruits)
        
        # notify that the board is built
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
        Each cell is stored as YZ in the map file, 
        with Y being the type of cell (- for walkable, E for entrance),
        and Z being the direction to go next in the path (U,D,L,R).
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
        load_cells_count = 0 # track how many loading cells are present
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
                elif waypoint == 'K':
                    cell = Cell(self, coords, path_direction, iskill=True)
                    kill_cell = cell
                elif waypoint == 'T':
                    cell = Cell(self, coords, path_direction, istrap=True)
                    trap_cell = cell
                else:
                    cell = Cell(self, coords, path_direction)
                # check if loading cell
                if len(line[j]) > 2:
                    load_dir = line[j][2] # direction to move fruits to when recipe match
                    load_cells_count += 1
                    cell.load_dir = load_dir
                tmprow.append(cell)

            cellgrid.append(tmprow)
        
        # check there's at least one of each cell
        if not entr_cell or not junc_cell or not wait_cell\
            or not kill_cell or not trap_cell:
            logging.critical('Board %s is missing waypoints' % filename)

        return (height, width, cellgrid,
                entr_cell, junc_cell, wait_cell, kill_cell, trap_cell,
                load_cells_count)
        

    
    def _build_path(self, waitzone_length):
        """ Build the path: link cells to each other.
        Shorten the exit path if it is longer in the map file 
        than the longest recipe for this level. 
        """
        
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

        # wire loading cells to exit cells
        cell = self.W
        load_dir = cell.load_dir
        i = waitzone_length
        while i > 0 and load_dir: # stops when a cell has no 2nd path direction
            cell.set_waitingpath()
            loadcoords = self._get_coords_from_dir(cell.coords, load_dir)
            loadcell = self.get_cell(loadcoords) 
            cell.loadcell = loadcell # wire
            cell = cell.prevcell
            load_dir = cell.load_dir
            i -= 1
        first_cell_exit_path = cell.nextcell.loadcell
        if i > 0:
            logging.critical('Longest recipe has %d fruits, ' % (waitzone_length)
                          + 'but exit path has fewer exit cells')
            exit()
        elif load_dir: # when exit path is longer than the longest recipe,
            # shorten the exit path 
            while load_dir:
                loadcoords = self._get_coords_from_dir(cell.coords, load_dir)
                loadcell = self.get_cell(loadcoords) 
                loadcell.set_nonwalkable()
                cell = cell.prevcell
                load_dir = cell.load_dir
            
         
        # build the path in the exit cells
        cell = first_cell_exit_path
        while cell != self.K:
            cell.set_exitpath()
            nextcoords = self._get_coords_from_dir(cell.coords, cell.pathdir)
            nextcell = self.get_cell(nextcoords)
            # wire
            cell.nextcell = nextcell
            nextcell.prevcell = cell
            # and keep going
            cell = nextcell
        self.K.set_exitpath() # K is also part of the exit path
        
        # wire the trap
        trap = self.T
        target_coords = self._get_coords_from_dir(trap.coords, trap.pathdir)
        target_cell = self.get_cell(target_coords)
        trap.set_target(target_cell)        

    
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
        """ Move the fruits if it's time to do so. """
        
        elapsed_millis = tickevt.loopduration
        self.fruit_mvt_timer -= elapsed_millis
        if self.fruit_mvt_timer <= 0:
            self._progress_fruits()
            self.fruit_mvt_timer = 1000. / self.fruit_speed
            
            
            
    def _progress_fruits(self):
        """ Make the fruits move on the board. """
        
        # blender/kill cell
        kcell = self.K
        kfruit = kcell.fruit
        if kfruit: # to the blender!
            self.fruits.remove(kfruit)
            kcell.empty()
            ev = FruitKilledEvent(kfruit)
            self._em.publish(ev)
            logging.debug('removed fruit: %s' % (kfruit))
            
        # exit cells
        cell = kcell.prevcell
        while cell != None: # stops at X.prevcell, which is None
            cell.progress_fruit()
            cell = cell.prevcell

        # waiting cell
        wcell = self.W
        wfruit = wcell.fruit
        # Stashing a fruit allows a full loop area to still be able to move.
        stashed_fruit = None
        if wfruit:
            # get all the fruits in the waiting cells
            wzone_fruits = self._get_waitingzone_fruits()
            # ask the game if there's any recipe matching
            num_fruits_to_kill = self.game.recipe_match(wzone_fruits)
            
            if num_fruits_to_kill == -1:# beginning of a match 
                # all fruits until the hole must wait
                for fruit in wzone_fruits:
                    if fruit:
                        fruit.wait()
                    else:    
                        break # fruits after the hole remain looping                            
                
            elif num_fruits_to_kill == 0: # no recipe match: keep moving!
                wcell.empty()
                stashed_fruit = wfruit # stash wfruit to allow for loop movement
                for fruit in wzone_fruits:
                    if fruit:
                        fruit.loop()
                    else:
                        break # fruits after the hole are looping already
                
            elif num_fruits_to_kill > 0: # recipe match!
                # exit some fruits
                cell = wcell
                for i in range(num_fruits_to_kill):
                    wzone_fruits[i].leave()
                    cell.exit_fruit()
                    cell = cell.prevcell
                    
                # the other fruits keep looping
                for i in range(num_fruits_to_kill, self.waitzone_length): 
                    fruit = wzone_fruits[i] # None if hole
                    if fruit:
                        fruit.loop()
                    else:
                        break # fruits after the hole are looping already
               
        # looping cells
        cell = wcell.prevcell
        while cell != wcell:
            fruit = cell.fruit
            if fruit and not fruit.is_waiting: # waiting fruits don't move
                cell.progress_fruit()
            cell = cell.prevcell
        
        # now we can put the stashed fruit (if any) back in the loop
        if stashed_fruit:
            wcell.nextcell.set_fruit(stashed_fruit, wcell)
          
        # entrance cells
        cell = self.J
        while cell != self.E.prevcell: # E.prevcell is None
            fruit = cell.fruit
            if fruit:
                if cell.nextcell.fruit: # fruit ahead: wait
                    fruit.wait()
                else:# no fruit ahead: can move
                    fruit.loop()
                    cell.progress_fruit()
            cell = cell.prevcell

        # tick the fruit spawner; must happen after all moves have been resolved        
        spawned, fruit = self.spawner.tick()
        if spawned:
            if fruit:
                self.fruits.add(fruit)
            else:
                logging.info('game over') # TODO: QuitEvent
                
        ev = BoardUpdatedEvent()
        self._em.publish(ev)



    def _get_waitingzone_fruits(self):
        """ Return the fruits in the waiting cells """
        fruit_list = []
        tmp_cell = self.W
        for _ in range(self.waitzone_length):
            fruit_list.append(tmp_cell.fruit) # fruit can be None
            tmp_cell = tmp_cell.prevcell
        return fruit_list


    def on_triggertrap(self, inputevt):
        """ User pushed the trap key. Try to trap a fruit. """
        caught = self.T.trap()
        
        
        
    def on_faster_fruits(self, ev):
        """ Increase the speed of the fruits """
        self.fruit_speed += .2 # by 0.2 cell per sec
        ev = FruitSpeedEvent(self.fruit_speed)
        self._em.publish(ev)

    def on_slower_fruits(self, ev):
        """ Decrease the speed of fruits """
        self.fruit_speed -= .2
        ev = FruitSpeedEvent(self.fruit_speed)
        self._em.publish(ev)
