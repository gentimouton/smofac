#! /usr/bin/env python3.2
import pygame
from pygame.locals import KEYDOWN, K_ESCAPE, QUIT


def main():

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Smoothie Factory')
    
    # create and display bg
    bg = pygame.Surface(screen.get_size())
    bg = bg.convert()
    bg.fill((250, 111, 111))
    screen.blit(bg, (0, 0))
    pygame.display.flip()
    
    
    while 1:
        clock.tick(30)
    
        #Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
        
    
if __name__ == "__main__":
    main()
