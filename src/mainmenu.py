from component import InputController, MenuDisplay
from mode import Mode
from events import QuitEvent, ToGameEvent, ValidateEvent, MoveUpEvent, \
    MoveDownEvent, MoveLeftEvent, MoveRightEvent
from pygame.locals import KEYDOWN, K_ESCAPE, QUIT, K_SPACE, K_EQUALS, K_PLUS, \
    K_MINUS, K_UNDERSCORE, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_RETURN
from pygame.sprite import LayeredDirty, LayeredDirty
import pygame


        

class MainMenuDisplay(MenuDisplay):
    evtlabels = [('game', ToGameEvent),
                 ('quit', QuitEvent)
                 ]

class MainMenuInputController(InputController):
    input_map = {K_ESCAPE: QuitEvent,
                 K_RETURN: ValidateEvent,
                 K_UP: MoveUpEvent,
                 K_DOWN: MoveDownEvent,
                 K_LEFT: MoveLeftEvent,
                 K_RIGHT: MoveRightEvent,
                 }

class MainMenuMode(Mode):
    components = [MainMenuDisplay, MainMenuInputController]

