
LOOPING = 'looping' # in the board loop
LEAVING = 'leaving' # on (or scheduled for) the exit path, 
WAITING = 'waiting' # standing still


class Fruit():
    """ The model part of a fruit """
    
    def __init__(self, fruit_type, fruit_num):
        
        self.fruit_type = fruit_type # 'S' for strawberry
        self.fruit_num = fruit_num
        self.loop()
        
        # fruit's model position; all cells are set by the board 
        self.cell = None
        self.prevcell = None
        self.nextcell = None


    def __repr__(self):
        if self.cell:
            return '%s#%d at %s %s' % (self.fruit_type, self.fruit_num,
                                      str(self.cell.coords), self.state)
        else:
            return '%s#%d %s' % (self.fruit_type, self.fruit_num,
                                      self.state)
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
        
           
