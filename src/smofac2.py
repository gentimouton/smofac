#! /usr/bin/env python3.2
from game2 import GameMode
from mainmenu import MainMenuMode
from mode import ModeStateMachine
from events import ToGameEvent, ToMenuEvent
import logging




def main():
    logging.basicConfig(level=logging.INFO)
    
    mm_mode = MainMenuMode()
    g_mode = GameMode()

    transitions = {mm_mode: {ToGameEvent: g_mode},
                   g_mode: {ToMenuEvent: mm_mode}
                   }
    
    msm = ModeStateMachine(mm_mode, [mm_mode, g_mode], transitions)



if __name__ == "__main__":
    main()



