#! /usr/bin/env python3.2
from events import ToGameEvent, ToMenuEvent, TriggerTrapEvent, \
    AccelerateFruitsEvent, DecelerateFruitsEvent, QuitEvent, ValidateEvent, \
    MoveUpEvent, MoveDownEvent, MoveLeftEvent, MoveRightEvent, GameWonEvent
from gamemodel import GameModel
from gameview import GameView
from input import InputController
from menuview import MenuView
from mode import ModeStateMachine, Mode
from pygame.locals import K_ESCAPE, K_SPACE, K_EQUALS, K_PLUS, K_MINUS, \
    K_UNDERSCORE, K_RETURN, K_UP, K_DOWN, K_LEFT, K_RIGHT
import logging


###################################################

class GameInputController(InputController):
    input_map = {K_ESCAPE: ToMenuEvent,
                 K_SPACE: TriggerTrapEvent,
                 K_EQUALS: AccelerateFruitsEvent,
                 K_PLUS:AccelerateFruitsEvent,
                 K_MINUS: DecelerateFruitsEvent,
                 K_UNDERSCORE: DecelerateFruitsEvent
                 }


class GameMode(Mode):
    components = [GameView, GameModel, GameInputController]

#####################################################

class MainMenuView(MenuView):
    evtlabels = [('game', ToGameEvent),
                 ('quit', QuitEvent)
                 ]
    pagename = 'Main Menu'

class MainMenuInputController(InputController):
    input_map = {K_ESCAPE: QuitEvent,
                 K_RETURN: ValidateEvent,
                 K_UP: MoveUpEvent,
                 K_DOWN: MoveDownEvent,
                 K_LEFT: MoveLeftEvent,
                 K_RIGHT: MoveRightEvent,
                 }

class MainMenuMode(Mode):
    components = [MainMenuView, MainMenuInputController]
    
#####################################################

def main():
    logging.basicConfig(level=logging.INFO)
    
    mm_mode = MainMenuMode()
    g_mode = GameMode()

    transitions = {mm_mode: {ToGameEvent: g_mode},
                   g_mode: {ToMenuEvent: mm_mode, GameWonEvent: mm_mode}
                   }
    
    msm = ModeStateMachine(g_mode, [mm_mode, g_mode], transitions)


if __name__ == "__main__":
    main()

