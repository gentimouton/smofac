from cell import Cell
from constants import DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT, FRUIT_SPEED
from events import BoardBuiltEvent, TickEvent, BoardUpdatedEvent, \
    PRIO_TICK_MODEL, FruitKilledEvent, AccelerateFruitsEvent, DecelerateFruitsEvent, \
    FruitSpeedEvent, FruitSpawnedEvent, BoardPredictedEvent, FruitPlacedEvent
from input import TriggerTrapEvent
from spawner import Spawner
import logging
import os
import time


        
class Board():
    
    def __init__(self, game, em, mapname, waitzone_length):
        """ Build the board. """
        
        self.mapname = mapname
        self.game = game
        self.phase = 'progress'
        
        # build the map
        loaded_map = self.__load_mapfile(mapname)
        self.height, self.width, self._cellgrid = loaded_map[0:3]
        self.E, self.J, self.W, self.K, self.T = loaded_map[3:8] 
        load_cells_count = loaded_map[8] # number of cells in loading zone
        if load_cells_count < waitzone_length:
            logging.warn('Longest recipe has %d fruits,' % waitzone_length
                         + ' but the map has only %d loading cells' 
                         % load_cells_count)
        self.waitzone_length = waitzone_length
        
        self.__build_path(waitzone_length)
        
        self.fruits = set()
        self.fruits_to_spawn = set()
        self.fruits_to_kill = set()
        self.fruits_to_move = set()
        
        # When it reaches zero or below, move the fruits.
        self.spawner = Spawner(em, self.E)

        self._em = em
        em.subscribe(TriggerTrapEvent, self.on_triggertrap)
        em.subscribe(FruitSpawnedEvent, self.on_fruit_spawned)
        
        # notify that the board is built
        ev = BoardBuiltEvent(self.width, self.height, self)
        em.publish(ev)
        

    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return '%s, %d x %d' % (self.filename, self.width, self.height)
            


    def __load_mapfile(self, filename):
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
        kill_cell = trap_cell = None
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
            logging.critical('Board %s is missing some waypoints' % filename)
            exit()

        return (height, width, cellgrid,
                entr_cell, junc_cell, wait_cell, kill_cell, trap_cell,
                load_cells_count)
        

    
    def __build_path(self, waitzone_length):
        """ Build the path: link cells to each other.
        Shorten the exit path if it is longer in the map file 
        than the longest recipe for this level. 
        """
        
        # entrance and loop areas
        cell = self.E 
        while not cell.nextcell: # ends when the loop is linked  
            nextcoords = self.get_coords_from_dir(cell.coords, cell.pathdir)
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
            loadcoords = self.get_coords_from_dir(cell.coords, load_dir)
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
                loadcoords = self.get_coords_from_dir(cell.coords, load_dir)
                loadcell = self.get_cell(loadcoords) 
                loadcell.set_nonwalkable()
                cell = cell.prevcell
                load_dir = cell.load_dir
            
         
        # build the path in the exit cells
        cell = first_cell_exit_path
        while cell != self.K:
            cell.set_exitpath()
            nextcoords = self.get_coords_from_dir(cell.coords, cell.pathdir)
            nextcell = self.get_cell(nextcoords)
            # wire
            cell.nextcell = nextcell
            nextcell.prevcell = cell
            # and keep going
            cell = nextcell
        self.K.set_exitpath() # K is also part of the exit path
        
        # wire the trap
        trap = self.T
        target_coords = self.get_coords_from_dir(trap.coords, trap.pathdir)
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
        
        
    def get_coords_from_dir(self, coords, direction):
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
        else: # no direction: cell is missing
            logging.critical('Cell %s does not seem walkable in map %s'
                             % (str(coords), self.mapname))
            exit()
        return c
    
            
            
    def progress_fruits(self):
        """ Actually move the fruits on the board. Aka movement tick.
        The loading cells are taken care of during the prediction tick. 
        """
        
        # kill fruits as soon as they land on the blender cell
        kcell = self.K
        kfruit = kcell.fruit
        if kfruit: # to the blender!
            cell = kfruit.cell
            self.fruits.remove(kfruit)
            cell.empty()
            ev = FruitKilledEvent(kfruit)
            self._em.publish(ev)
            logging.debug('removed fruit: %s' % kfruit)
        
        # exit cells
        cell = kcell.prevcell
        while cell != None: # stops at X.prevcell, which is None
            cell.move_fruit()
            cell = cell.prevcell

        # waiting cell
        wcell = self.W
        wfruit = wcell.fruit
        # Stashing a fruit allows a full loop area to still be able to move.
        stashed_fruit = None
        if wfruit:
            if wfruit.is_leaving: # wfruit has been predicted to leave
                wcell.move_fruit() # wfruit.nextcell should be an exit cell
            elif wfruit.is_looping: # prediction tick says wfruit should loop
                stashed_fruit = wfruit
                wcell.empty()
            
        # looping cells
        cell = wcell.prevcell
        while cell != wcell:
            fruit = cell.fruit
            if fruit and not fruit.is_waiting: # waiting fruits don't move
                # fruits are set to wait by the prediction tick
                cell.move_fruit()
            cell = cell.prevcell
        
        # now we can put the stashed fruit (if any) back in the loop
        if stashed_fruit:
            cell = wcell.nextcell
            cell.set_fruit(stashed_fruit)
          
        # entrance cells
        cell = self.J
        while cell != self.E.prevcell: # E.prevcell is None
            cell.move_fruit()
            cell = cell.prevcell
        
        self.phase = 'progress'
        ev = BoardUpdatedEvent()
        self._em.publish(ev)

        
        
    def predict_fruits(self):
        """ Predict the next cell each fruit is going to be in. 
        Aka prediction tick.
        """
        
        # nothing to do for the blender cell: 
        # the fruit has been killed at movement tick
          
        # exit cells
        cell = self.K.prevcell
        while cell != None: # stops at X.prevcell, which is None
            cell.predict_fruit_move()
            cell = cell.prevcell

        # waiting cells
        wcell = self.W
        # get all the fruits in the waiting cells
        wzone_fruits = self.get_waitingzone_fruits()

        # ask the game if there's any recipe matching
        should_wait, num_fruits_to_kill = self.game.recipe_match(wzone_fruits)
        # iterate over the waiting cells
        i = self.waitzone_length
        cell = wcell
        # all fruits until the hole must wait; 
        # fruits after the hole must loop
        
        if should_wait:# beginning of a match 
            seen_hole = False
            while i > 0:
                fruit = cell.fruit
                if seen_hole: # fruits after the hole remain looping
                    if fruit: # can be None if the cell has no fruit
                        fruit.loop()
                        cell.predict_fruit_move()
                else:# all loading cells so far had fruits
                    if fruit:
                        fruit.wait()
                    else: # first cell without fruit: hole seen!
                        seen_hole = True
                cell = cell.prevcell
                i -= 1
            
        else:
            j = num_fruits_to_kill
            while i > 0:
                fruit = cell.fruit
                if j > 0: # fruits part of the recipe leave
                    if fruit:
                        fruit.leave()
                        cell.predict_fruit_exit()
                    j -= 1
                else: # the other fruits keep looping
                    if fruit:
                        fruit.loop()
                        cell.predict_fruit_move()
                cell = cell.prevcell
                i -= 1
                        
        # at this line, cell is the first non-waiting cell
        # non-waiting looping cells
        while cell != wcell:
            fruit = cell.fruit
            if fruit and fruit.is_looping: # waiting fruits dont move
                # and leaving fruits have been taken care of above
                cell.predict_fruit_move()
            cell = cell.prevcell
        
        # entrance cells
        jcell = self.J
        jfruit = jcell.fruit
        if jfruit:
            if jcell.nextcell.prevcell.fruit:
                jfruit.wait()
            else:
                jfruit.loop()
                jcell.predict_fruit_move()
        
        cell = jcell.prevcell
        while cell != self.E.prevcell: # E.prevcell is None
            fruit = cell.fruit
            if fruit:
                next_fruit = cell.nextcell.fruit
                if next_fruit and next_fruit.is_waiting: 
                    # fruit waiting ahead: wait
                    fruit.wait()
                else:# no waiting fruit ahead: can loop
                    fruit.loop()
                    cell.predict_fruit_move()
            cell = cell.prevcell
        
        self.phase = 'predict'
        ev = BoardPredictedEvent()
        self._em.publish(ev)



    def get_waitingzone_fruits(self):
        """ Return the fruits in the waiting cells """
        fruit_list = []
        tmp_cell = self.W
        for _ in range(self.waitzone_length):
            fruit_list.append(tmp_cell.fruit) # fruit can be None
            tmp_cell = tmp_cell.prevcell
        return fruit_list


    def on_fruit_spawned(self, ev):
        """ When a fruit is spawned, add it to the list. """
        
        entrance = self.E
        if entrance.fruit: # should spawn new fruit, but can't: game over!
            logging.info('game over') # TODO: QuitEvent
        
        else: # if there's room
            fruit = ev.fruit
            fruit.cell = entrance
            fruit.prevcell = entrance
            if self.phase == 'progress':
                fruit.nextcell = None
            else: # phase is 'predict'
                fruit.nextcell = entrance.nextcell
            entrance.fruit = fruit
            if entrance.nextcell.fruit:
                fruit.wait()
            self.fruits.add(fruit)
            ev = FruitPlacedEvent(fruit)
            self._em.publish(ev)
            
                
        
    def on_triggertrap(self, ev):
        """ User pushed the trap key. Try to trap a fruit. """
        is_predict_phase = self.phase == 'predict'
        self.T.do_trap(is_predict_phase)
        
        
