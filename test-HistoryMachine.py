from scm import StateMachineManager

watch_scxml = """\
   <scxml non-unique='on,off'> 
       <state id='time'> 
            <transition event='a' target='alarm1'/> 
            <transition event='c_down' target='wait'/> 
       </state> 
       <state id='wait'> 
            <transition event='c_up' target='time'/> 
            <transition event='2_sec' target='update'/> 
       </state> 
       <state id='update'> 
            <history id='histu' type='shallow'/> 
            <transition event='d' target='histu'/> 
            <state id='sec'> 
                <transition event='c' target='1min'/> 
            </state> 
            <state id='1min'> 
                <transition event='c' target='10min'/> 
            </state> 
            <state id='10min'> 
                <transition event='c' target='hr'/> 
            </state> 
            <state id='hr'> 
                <transition event='c' target='time'/> 
            </state> 
       </state> 
       <state id='alarm1' history='shallow'> 
            <transition event='a' target='alarm2'/> 
            <state id='off' > 
                <transition event='d' target='on'/> 
            </state> 
            <state id='on' > 
                <transition event='d' target='off'/> 
            </state> 
       </state> 
       <state id='alarm2' history='shallow'> 
            <transition event='a' target='chime'/> 
            <state id='off' > 
                <transition event='d' target='on'/> 
            </state> 
            <state id='on' > 
                <transition event='d' target='off'/> 
            </state> 
       </state> 
       <state id='chime' history='shallow'> 
            <transition event='a' target='stopwatch'/> 
            <state id='off' > 
                    <transition event='d' target='on'/> 
            </state> 
            <state id='on' > 
                <transition event='d' target='off'/> 
            </state> 
       </state> 
       <state id='stopwatch' history='deep'> 
            <transition event='a' target='time'/> 
            <state id='zero'> 
                <transition event='b' target='on,regular'/> 
            </state> 
            <parallel> 
                <state id='run'> 
                    <state id='on' > 
                        <transition event='b' target='off'/> 
                    </state> 
                    <state id='off' > 
                        <transition event='b' target='on'/> 
                    </state> 
                </state> 
                <state id='display'> 
                    <state id='regular'> 
                        <transition event='d' cond='In(on)' target='lap'/> 
                        <transition event='d' cond='In(off)' target='zero'/> 
                    </state> 
                    <state id='lap'> 
                        <transition event='d' target='regular'/> 
                    </state> 
                </state> 
            </parallel> 
       </state> 
    </scxml> 
"""

class TheMachine:
    def __init__(self):
        self.mach_ = StateMachineManager.instance().getMach("watch")
        self.hr_ = 0
        self.min_ = 0
        self.sec_ = 0
        
        states = self.mach_.get_all_states()
        print('we have states:')
        
        for state in states:
            st = self.mach_.getState(state)
            if not st:   # <- state machine itself
                continue
            print('    ' * st.depth(), state)
            self.mach_.setActionSlot('onentry_'+state, lambda : self.onentry_report_state(False) )
            self.mach_.setActionSlot('onexit_'+state, lambda s=state: self.onexit_report_state(s) )
        print('')
        self.mach_.setActionSlot('onentry_sec', self.onentry_sec)
        self.mach_.setActionSlot('onentry_1min', self.onentry_1min)
        self.mach_.setActionSlot('onentry_10min', self.onentry_10min)
        self.mach_.setActionSlot('onentry_hr', self.onentry_hr)

        self.mach_.StartEngine()
        
        
    def onentry_sec(self):
        if self.mach_.re_enter_state():
            self.sec_ = 0        
        self.onentry_report_state(True)
    
    def onentry_1min(self):
        if self.mach_.re_enter_state():
            self.min_ += 1
        self.onentry_report_state(True)
    
    def onentry_10min(self):
        if self.mach_.re_enter_state():
            self.min_ += 10
        self.onentry_report_state(True)
    
    def onentry_hr(self):
        if self.mach_.re_enter_state():
            self.hr_ += 1
        self.onentry_report_state(True)
    
    def onentry_report_state(self, with_time):
        print("enter state ", self.mach_.getEnterState().state_uid(), end='')
        #if with_time:
        print(". time ", self.hr_, ":", self.min_, ":", self.sec_, end='')
        
        print('')
        self.sec_ += 1
    
    def onexit_report_state(self, st):
        print("exit state ", st)
    
    def test (self):
        # time
        self.mach_.enqueEvent("c_down") # -> wait
        self.mach_.enqueEvent("2_sec") # -> update, you will use registerTimedEvent to generate event after 2 seconds
        self.mach_.enqueEvent("d") #  reset, 1 second
        self.mach_.enqueEvent("d") #  reset, 1 second
        self.mach_.enqueEvent("d") #  reset, 1 second
        self.mach_.enqueEvent("c") # -> 1min state
        self.mach_.enqueEvent("d") #  1 min
        self.mach_.enqueEvent("d") #  2 min
        self.mach_.enqueEvent("c") # -> 10min state
        self.mach_.enqueEvent("d") #  12 min
        self.mach_.enqueEvent("c") # -> hr state
        self.mach_.enqueEvent("d") #  1 hr
        self.mach_.enqueEvent("d") #  2 hr
        self.mach_.enqueEvent("c") # -> time
        
        self.mach_.enqueEvent("a") # -> alarm1
        self.mach_.enqueEvent("d")
        self.mach_.enqueEvent("a") # -> alarm2
        self.mach_.enqueEvent("d")
        self.mach_.enqueEvent("a") # -> chime
        self.mach_.enqueEvent("d")
        self.mach_.enqueEvent("a") # -> stopwatch.zero
        self.mach_.enqueEvent("b") # -> run.on
        self.mach_.enqueEvent("d") # -> display.lap
        self.mach_.enqueEvent("a") # -> time
        self.mach_.enqueEvent("d") # no effect
        self.mach_.enqueEvent("a") # -> alarm1
        self.mach_.enqueEvent("d")
        self.mach_.enqueEvent("a") # -> alarm2
        self.mach_.enqueEvent("d")
        self.mach_.enqueEvent("a") # -> chime
        self.mach_.enqueEvent("d")
        self.mach_.enqueEvent("a") # -> stopwatch, what's run and display in?
        
        self.mach_.frame_move(0)

if __name__ == '__main__':
    StateMachineManager.instance().set_scxml("watch", watch_scxml)
    mach = TheMachine()
    mach.test()
    StateMachineManager.instance().pumpMachEvents()

