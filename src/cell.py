from config import trap_color, path_color, bg_color, blender_color, cell_size
from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame.surface import Surface
import logging

class Cell(Sprite):
    """ TODO: split into gfx and model parts. """

    def __init__(self, board, coords, pathdir, iswalkable, isentr=False,
                 isjunc=False, iswait=False, iskill=False, istrap=False):
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
        self.iswalkable = iswalkable # traps are walkable
        self.istrap = istrap
        self.load_dir = None

        #gfx
        cspr_left = left * cell_size
        cspr_top = top * cell_size
        self.rect = Rect(cspr_left, cspr_top, cell_size, cell_size)
        img = Surface((cell_size, cell_size))

        if istrap:
            img.fill(trap_color)
        elif self.iswalkable: # but not a trap
            img.fill(path_color)
        else:
            img.fill(bg_color)

        self.image = img


    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        if self.fruit:
            fruitdata = 'FRUIT'
        else:
            fruitdata = 'NOFRUIT'
        return '%s' % (str(self.coords)) + fruitdata


    @property
    def direction(self):
        """ Return the direction where the next cell is. """
        return self.pathdir

    def set_exitpath(self):
        """ The board found out that I am on the exit path. 
        Change my color. """
        self.image.fill(blender_color)

    def set_waitingpath(self):
        """ The board found out I'm a cell in the waiting area. 
        Change my color. """
        self.image.fill(blender_color)

    def set_nonwalkable(self):
        """ The board found out there are more cells in the exit path
        than the longest recipe: some cells (like me) need to be removed """
        self.iswalkable = False
        self.image.fill(bg_color)


    #################### fruit stuff

    def empty(self):
        """ Remove my fruit """
        self.fruit = None


    def set_fruit(self, fruit):
        """ Add a fruit to my cell. Called during movement tick. """
        if self.fruit:
            logging.error('Trying to add fruit %s to cell %s,' % (fruit, self)\
                          + ' but it already has fruit %s' % self.fruit)
        # replace in any case
        fruit.prevcell = fruit.cell
        fruit.cell = self
        fruit.nextcell = None # tell to the view that we're in movement phase
        self.fruit = fruit


    def move_fruit(self):
        """ Actually move a fruit. """
        myfruit = self.fruit
        if myfruit and not myfruit.is_waiting:
            # The fruit's next cell has been predicted 
            # by the previous prediction tick.
            tcell = myfruit.nextcell # AND NOT self.nextcell!!!
            myfruit.cell = tcell
            myfruit.nextcell = None # indicates we're in movement phase to the view
            myfruit.prevcell = self
            tcell.fruit = myfruit
            self.fruit = None

    def predict_fruit_move(self, cell=None):
        """ Predict the next cell of my fruit. 
        If a cell is specified, predict to that cell instead. 
        """
        myfruit = self.fruit
        if myfruit:
            tcell = cell or self.nextcell
            myfruit.nextcell = tcell # indicates we're in prediction phase to the view


    def exit_fruit(self):
        """ Move a fruit to my exit cell. """
        if not self.loadcell:
            logging.error('Cell %s can not exit a fruit ' % self\
                          + ' because it is not connected to any exit cell.')
        myfruit = self.fruit
        if myfruit:
            loadcell = self.loadcell
            loadcell.fruit = myfruit
            myfruit.move_to(loadcell)
            self.fruit = None
        else:
            logging.warn('Cell %s tried to exit a fruit ' % self\
                         + 'but it does not have any fruit.')


    def predict_fruit_exit(self):
        """ Predict the next exit cell of my fruit. """
        myfruit = self.fruit
        if myfruit:
            if not self.loadcell:
                logging.error('Cell %s tried to predict' % self\
                              + ' the exit of fruit %s' % myfruit\
                              + ' but it is not linked to a loading cell.')
            myfruit.nextcell = self.loadcell


    ################# trap stuff


    def set_target(self, targetcell):
        """ Called when the board wires the path. 
        When the cell is a trap, 
        its target is the cell it is stealing from. """
        self.target = targetcell


    def do_trap(self, is_predict_phase):
        """ Try to catch/release/swap a fruit from/to/with the target cell.
        """
        myfruit = self.fruit
        tcell = self.target
        tfruit = tcell.fruit

        if myfruit:
            if tfruit: # swap
                # my fruit
                myfruit.prevcell = tcell.prevcell
                myfruit.cell = tcell
                if is_predict_phase:
                    myfruit.nextcell = tcell.nextcell
                else:
                    myfruit.nextcell = None
                myfruit.loop()
                tcell.fruit = myfruit
                # target fruit
                tfruit.nextcell = None
                tfruit.prevcell = tcell
                tfruit.cell = self
                tfruit.wait()
                self.fruit = tfruit


            else: # release
                myfruit.prevcell = tcell.prevcell
                myfruit.cell = tcell
                if is_predict_phase:
                    myfruit.nextcell = tcell.nextcell
                else:
                    myfruit.nextcell = None
                myfruit.loop()
                tcell.fruit = myfruit
                self.fruit = None


        else: # I have no fruit
            if tfruit: # catch
                tfruit.nextcell = None
                tfruit.prevcell = tcell
                tfruit.cell = self
                tfruit.wait()
                self.fruit = tfruit
                tcell.empty()

