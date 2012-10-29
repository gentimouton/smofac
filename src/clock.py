from config import fps
from events import CTickEvent, MTickEvent, VTickEvent
from time import time, sleep


class Clock():

    def __init__(self, em):
        self.fps = fps
        self._em = em
        self.elapsed_frames = 0


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
            whole_millis = wholeduration * 1000
            work_millis = workduration * 1000

            event = CTickEvent(whole_millis, work_millis)
            self._em.publish(event) # tick controllers
            event = MTickEvent(whole_millis, work_millis)
            self._em.publish(event) # tick models
            event = VTickEvent(whole_millis, work_millis)
            self._em.publish(event) # tick views

            aftertick = time()
            workduration = aftertick - beforetick

            sleepduration = 1 / self.fps - workduration
            sleepduration = max(0, sleepduration)
            if sleepduration > 0: # dont sleep if late 
                sleep(sleepduration)

            self.elapsed_frames += 1


    def stop(self):
        """ Stop the game """
        self.keep_going = False

