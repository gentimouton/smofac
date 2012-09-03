#! /usr/bin/env python3.2
from clock import Clock
from events import EventManager
from game import Game
from input import InputController
from view import PygameDisplay
import logging


def main():

    logging.basicConfig(level=logging.INFO)

    # init all components
    em = EventManager()
    
    view = PygameDisplay(em)
    game = Game(em)
    keyboard = InputController(em)
    
    clock = Clock(em)
    clock.start() # start the main loop
    
    
if __name__ == "__main__":
    main()
