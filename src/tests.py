from pygame.surface import Surface
from pygame.rect import Rect
from pygame.transform import rotate
from pygame.font import Font
import pygame
from time import sleep

pygame.init()
screen = pygame.display.set_mode((400, 400))
screen.fill((40, 40, 40))

CELLSIZE = 100

# make a cell
cell_rect = Rect(0, 0, CELLSIZE, CELLSIZE)
pygame.draw.rect(screen, (0, 255, 0), cell_rect)

ratio = 1.414 # how much bigger is the cell compared to the diamond

# make the red square
org_surf = Surface((CELLSIZE / ratio, CELLSIZE / ratio))
org_surf.set_colorkey((255, 0, 255))  # magenta = color key
org_surf.fill((255, 0, 0)) # fill with red

# blit the original
width = org_surf.get_rect().width
blit_rect = Rect(0, 0, width, width)
blit_rect.center = cell_rect.center
#screen.blit(org_surf, blit_rect)

# rotate to get a diamond
rot_surf = rotate(org_surf, 45)

# blit
width = org_surf.get_rect().width * ratio
blit_rect = Rect(0, 0, width, width)
blit_rect.center = cell_rect.center # blit diamond in the middle of the cell
screen.blit(rot_surf, blit_rect)



pygame.display.flip()

sleep(1)
exit()
