from constants import FRUIT_COLORS, FONT_SIZE, CELLSIZE
import pygame


class Fruit(pygame.sprite.Sprite):
    
    def __init__(self, cell, fruit_type, fruit_id):
        self.cell = cell
        self.fruit_type = fruit_type # 's' for strawberry
        self.fruit_id = fruit_id
        self.isleaving = False
        
        # fill with color and write fruit number 
        self.surf = pygame.Surface((CELLSIZE * 4 / 5, CELLSIZE * 4 / 5))
        self.surf.fill(FRUIT_COLORS[fruit_type])
        self.font = pygame.font.Font(None, FONT_SIZE) 
        txtsurf = self.font.render(str(fruit_id), True, (0, 0, 0))
        textpos = txtsurf.get_rect(centerx=self.surf.get_width() / 2,
                                   centery=self.surf.get_height() / 2)
        self.surf.blit(txtsurf, textpos)

        self.update()
        
    
    def __repr__(self):
        return '%s#%d at %s' % (self.fruit_type,
                                self.fruit_id,
                                str(self.cell.coords))
    def __str__(self):
        return self.__repr__()
        

    def update(self):
        left, top = self.cell.coords
        self.rect = pygame.Rect(left * CELLSIZE + 5, top * CELLSIZE + 5,
                                CELLSIZE * 4 / 5, CELLSIZE * 4 / 5)
        
