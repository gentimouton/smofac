#! /usr/bin/env python3.2
from board import Board
from pygame.locals import KEYDOWN, K_ESCAPE, QUIT, K_SPACE
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
        clock.tick(2)
    
        # handle inputs
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_SPACE:
                    board.trap()
                    
        # update board
        isgameover = board.update()
        pygame.display.flip()
        
        if isgameover:
            logging.info('game over')
            return
    
    
if __name__ == "__main__":
    main()
