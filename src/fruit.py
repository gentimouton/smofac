from constants import FRUIT_COLORS
import pygame


class Fruit(pygame.sprite.Sprite):
    
    def __init__(self, cell, fruit_type, fruit_id):
        self.cell = cell
        self.fruit_type = fruit_type # 's' for strawberry
        self.fruit_id = fruit_id
        self.isleaving = False
        
        self.image = pygame.Surface((50, 50))
        self.image.fill(FRUIT_COLORS[fruit_type])
        self.update()
        
    
    def __repr__(self):
        return 'Fruit at %s' % (str(self.cell.coords))
    def __str__(self):
        return self.__repr__()
        

    def update(self):
        left, top = self.cell.coords
        self.rect = pygame.Rect(left * 50, top * 50, 50, 50)
        
