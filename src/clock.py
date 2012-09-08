from constants import FPS
from events import QuitEvent, TickEvent
from time import sleep, time
import logging



class Clock():
    
    def __init__(self, em):
        self.fps = FPS
        self._em = em
        self.elapsed_frames = 0
        
        self._em.subscribe(QuitEvent, self.on_quit)
        
    
    def start(self):
        """ When all actions are done, wait for a few milliseconds. 
        This makes the frequency *at most* as fast as the specified frame rate.
        Frames with more work may take longer than the specified frame rate. 
        """
        self.keep_going = True
        sleepduration = workduration = 0
                
        while self.keep_going:
            beforetick = time()
            wholeduration = (sleepduration + workduration)
            event = TickEvent(wholeduration * 1000, workduration * 1000)
            self._em.publish(event) # tick all registered components

            aftertick = time()
            workduration = aftertick - beforetick #0 on first tick
            sleepduration = 1 / self.fps - workduration
            sleepduration = max(0, sleepduration)# dont sleep if late
            if sleepduration > 0: 
                sleep(sleepduration)

            self.elapsed_frames += 1
    


    
    def on_quit(self, ev):
        """ Stop the game! """
        self.keep_going = False
        
