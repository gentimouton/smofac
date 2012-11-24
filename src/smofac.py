#! /usr/bin/env python3.2

# configure the logger before anything else happens
import logging.config
logging.config.fileConfig('logging.conf')


# then import game stuffs
from events import StartNewGameEvent, ToMenuEvent, TriggerTrapEvent, \
    AccelerateFruitsEvent, DecelerateFruitsEvent, QuitEvent, ValidateEvent, \
    MoveUpEvent, MoveDownEvent, MoveLeftEvent, MoveRightEvent, GameWonEvent, \
    StartGameEvent
from gamemodel import GameModel
from gameview import GameView
from input import InputController
from menuview import MenuView
from mode import ModeStateMachine, Mode
from pygame.locals import K_ESCAPE, K_SPACE, K_EQUALS, K_PLUS, K_MINUS, \
    K_UNDERSCORE, K_RETURN, K_UP, K_DOWN, K_LEFT, K_RIGHT




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
    evtlabels = [('new game', StartNewGameEvent),
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


class LevelTransitionView(MenuView):

    def __init__(self, em, ev):
        """ if just completed level 2, only propose to go to main menu """

        lvlname = ev.lvlname # number of the level just completed
        self.pagename = 'level %s completed' % lvlname # window-bar title

        self.evtlabels = [('to main menu', ToMenuEvent)]
        if lvlname != 'lvl2': # there is a next level
            lvlnum = int(lvlname[-1])
            self.evtlabels.insert(0, ('next game', StartGameEvent,
                                      ['lvl%d' % (lvlnum + 1)]))

        MenuView.__init__(self, em, ev)


class LevelTransitionMode(Mode):
    components = [LevelTransitionView, MainMenuInputController]


########################################################

def main():

    # The smofac logger is configured when the config module is imported.
    log = logging.getLogger('smofac')
    log.info('Smofac started')

    mm_mode = MainMenuMode()
    g_mode = GameMode()
    lt_mode = LevelTransitionMode()

    transitions = {mm_mode: {StartNewGameEvent: g_mode},
                   g_mode: {ToMenuEvent: mm_mode, GameWonEvent: lt_mode},
                   lt_mode: {StartGameEvent: g_mode, ToMenuEvent: mm_mode}
                   }

    init_evt = StartNewGameEvent()

    msm = ModeStateMachine(transitions, g_mode, init_evt)


if __name__ == "__main__":
    main()

