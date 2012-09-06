from constants import FRUIT_COLORS, FONT_SIZE, CELLSIZE
import pygame

LOOPING = 'looping' # in the board loop
LEAVING = 'leaving' # on (or scheduled for) the exit path, 
WAITING = 'waiting' # standing still


class Fruit(pygame.sprite.Sprite):
    
    def __init__(self, cell, fruit_type, fruit_num):
        self.cell = cell
        self.fruit_type = fruit_type # 'S' for strawberry
        self.fruit_num = fruit_num
        self.state = LOOPING
        
        # graphics
        # fill with color and write fruit number 
        self.surf = pygame.Surface((CELLSIZE * 4 / 5, CELLSIZE * 4 / 5))
        self.surf.fill(FRUIT_COLORS[fruit_type])
        self.font = pygame.font.Font(None, FONT_SIZE) 
        txtsurf = self.font.render(str(fruit_num), True, (0, 0, 0))
        textpos = txtsurf.get_rect(centerx=self.surf.get_width() / 2,
                                   centery=self.surf.get_height() / 2)
        self.surf.blit(txtsurf, textpos)

        self.update()
        
    
    def __repr__(self):
        return '%s#%d %s at %s' % (self.fruit_type,
                                self.fruit_num,
                                self.state,
                                str(self.cell.coords))
    def __str__(self):
        return self.__repr__()
        

    def update(self):
        """ Reposition the rect to match the fruit's position. """
        left, top = self.cell.coords
        self.rect = pygame.Rect(left * CELLSIZE + CELLSIZE / 10 ,
                                top * CELLSIZE + CELLSIZE / 10,
                                CELLSIZE * 4 / 5,
                                CELLSIZE * 4 / 5)
        
