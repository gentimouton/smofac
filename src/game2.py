from component import InputController, MenuDisplay
from mode import Mode
from events import ValidateEvent, MoveUpEvent, MoveDownEvent, MoveLeftEvent, \
    MoveRightEvent, ToMenuEvent
from pygame.locals import K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_RETURN

class GameDisplay(MenuDisplay):
    evtlabels = [('back', ToMenuEvent),
                 ('back2', ToMenuEvent)
                 ]

class GameInputController(InputController):
    input_map = {K_ESCAPE: ToMenuEvent,
                 K_RETURN: ValidateEvent,
                 K_UP: MoveUpEvent,
                 K_DOWN: MoveDownEvent,
                 K_LEFT: MoveLeftEvent,
                 K_RIGHT: MoveRightEvent,
                 }

class GameMode(Mode):
    components = [GameDisplay, GameInputController]
