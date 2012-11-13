from clock import Clock
from events import EventManager, QuitEvent


class Mode:
    """ 
    A mode has its own clock, event manager, and components.
    A mode is a state activated and deactivated by the mode state machine.
    """

    def __repr__(self):
        return self.__class__.__name__
    def __str__(self):
        return self.__repr__()


    def __init__(self):
        """ When a mode is created, it only creates an event manager.
        The mode's components and clock are instantiated 
        when the mode is activated.
        The mode manager/MSM has to register for transition or quit callbacks 
        through set_X_callback.
        """

        # hold instances of the mode's components when the mode is activated
        self.active_components = []
        self.clock = None # instantiated by MSM
        self.em = EventManager() # each mode has its own EM


    def set_transition_callback(self, trans_evt_classes, msm_transition_cb):
        """ Set the callback to the mode state machine
        when transition events are fired by the current mode.
        """
        for ev_class in trans_evt_classes:
            self.em.subscribe(ev_class, msm_transition_cb)

    def set_quit_callback(self, msm_quit_cb):
        """ Set the MSM callback to call when the mode fires a QuitEvent. """
        self.em.subscribe(QuitEvent, msm_quit_cb)


    def activate(self, ev):
        """ Instantiate the components and clock for the mode. 
        The event passed in argument contains data sent by the previous mode.
        For example, the LevelTransitionMode sends a GameStart event
        containing the next level number to the GameMode. This way, the GameMode
        knows which level to instantiate. The GameMode sends a GameWon event
        containing the score to the LevelTransitionMode so that it can be 
        displayed.
        Small drawback: to keep the code generic, ALL the components are given 
        in argument the mode's EM and the event. Some components may not need 
        the event, but we can't know in advance, so we pass it anyway.
        """
        em = self.em
        self.active_components = [comp(em, ev) for comp in self.components]
        self.clock = Clock(em)
        self.clock.start() # returns when the clock is turned off, ie transition or quit 

        self.em.clear() # this removes the clock and MSM from the EM subscribers
        self.active_components = [] # last ref to component instances is lost
        self.clock = None


    def deactivate(self):
        """ Tell the clock to stop. 
        The mode's components will be garbage collected
        when the clock returns the hand back to the MSM. 
        """
        self.clock.stop()





class ModeStateMachine:
    """ Singleton in charge of transitions between modes.
    
    Needs to subscribe to each mode's event manager  
    to be able to perform transitions between modes as follows: 
    1) MSM receives the transition event from the current active mode;
    2) MSM stops the clock of the current active mode, 
    memorizes which mode is scheduled to go, and returns the hand;
    3) the event manager of the current mode finishes dispatching its events,
    the clock of the current mode finishes its tick,
    and the clock returns the hand to the mode, which returns the hand to MSM;
    4) MSM replaces its current mode by the scheduled new mode,
    and starts the clock of the new mode.
    
    When catching a QuitEvent, MSM stops the current mode's clock 
    and returns without switching to another mode, which stops the program.
    """


    def __repr__(self):
        return 'MSM(cur=%s)' % self.cur_mode
    def __str__(self):
        return self.__repr__()



    def __init__(self, init_mode, transitions):
        """ transitions is a dict mapping a mode instance
        to a dict(event class, mode instance).
        The keys of transitions are the mode states.
        """

        self.cur_mode = init_mode
        self.cur_mode_evt = None # event to pass as argument to the current mode
        self.modes = list(transitions.keys())
        self.transitions = transitions

        while self.cur_mode:
            # listen to transition and quit events 
            evt_classes = transitions[self.cur_mode].keys()
            self.cur_mode.set_transition_callback(evt_classes, self.on_transition)
            self.cur_mode.set_quit_callback(self.on_quit)

            self.cur_mode.activate(self.cur_mode_evt) # returns when the mode's clock stops

        # the current mode is changed when transition events are fired
        # if the current mode is None, the program exits
        #while self.cur_mode:
        #    self.cur_mode.set_quit_callback(self.on_quit)
        #    self.cur_mode.activate() # returns when the mode's clock stops



    def on_transition(self, ev):
        """ Callback when a mode transition event is fired by the current mode. 
        """
        new_mode = self.transitions[self.cur_mode][ev.__class__]
        self.cur_mode.deactivate()
        self.cur_mode = new_mode # cur_mode is activated in the while loop above
        self.cur_mode_evt = ev


    def on_quit(self, ev):
        """ Stop the current mode's clock. """
        self.cur_mode.deactivate()
        self.cur_mode = None


