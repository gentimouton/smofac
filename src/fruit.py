
LOOPING = 'looping' # in the board loop
LEAVING = 'leaving' # on (or scheduled for) the exit path, 
WAITING = 'waiting' # standing still


class Fruit():
    """ The model part of a fruit """
    
    def __init__(self, cell, fruit_type, fruit_num):
        
        self.fruit_type = fruit_type # 'S' for strawberry
        self.fruit_num = fruit_num
        self.loop()
        
        # fruit's model position. 
        self.cell = cell
        self.prevcell = cell


    def __repr__(self):
        return '%s#%d %s' % (self.fruit_type, self.fruit_num, self.state)
    def __str__(self):
        return self.__repr__()
        
    @property
    def coords(self):
        return self.cell.coords    
    @property
    def is_leaving(self):
        return self.state == LEAVING
    def leave(self):
        self.state = LEAVING
    @property
    def is_waiting(self):
        return self.state == WAITING
    def wait(self):
        self.state = WAITING
    @property
    def is_looping(self):
        return self.state == LOOPING
    def loop(self):
        self.state = LOOPING
    
        
    def grab_to(self, cell):
        """ When the fruit is captured, it becomes waiting. """
        self.cell = cell
        self.wait()
        
    def release_to(self, cell, swap=None):
        """ TODO: swapping """
        self.cell = cell
        self.loop()
        
    def move_to(self, cell):
        self.prevcell = self.cell
        self.cell = cell
