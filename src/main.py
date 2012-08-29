#! /usr/bin/env python3.2
from board import Board
from pygame.locals import KEYDOWN, K_ESCAPE, QUIT
import logging
import pygame

def main():

    logging.basicConfig(level=logging.DEBUG)

    pygame.init()
    clock = pygame.time.Clock()
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Smoothie Factory')

    board = Board('small.txt', screen)
    pygame.display.flip()
    
    
    while 1:
        clock.tick(30)
    
        #Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            
        board.display(screen)
        
    
if __name__ == "__main__":
    main()
