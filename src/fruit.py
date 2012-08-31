from constants import FRUIT_COLORS
import pygame


class Fruit(pygame.sprite.Sprite):
    
    def __init__(self, cell, fruit_type, fruit_id):
        self.cell = cell
        self.fruit_type = fruit_type # 's' for strawberry
        self.fruit_id = fruit_id
        self.isleaving = False
        
        # fill with color and write fruit number 
        self.surf = pygame.Surface((50, 50))
        self.surf.fill(FRUIT_COLORS[fruit_type])
        self.font = pygame.font.Font(None, 33) 
        txtsurf = self.font.render(str(fruit_id), True, (0,0,0))
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
        self.rect = pygame.Rect(left * 50, top * 50, 50, 50)
        
