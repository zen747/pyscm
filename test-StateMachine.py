from scm import StateMachineManager

client_scxml = """
   <scxml> 
       <state id='new'> 
           <transition event='punch' target='punching'/> 
       </state> 
       <parallel id='live'> 
            <state id='punch'> 
                <transition event='fail' target='punch_fail'/> 
                <state id='punching'> 
                    <transition event='linked' target='linked'/> 
                </state> 
                <state id='linked'> 
                    <transition event='established' target='punch_success'/> 
                </state> 
                <state id='punch_success'> 
                </state> 
                <state id='punch_fail'> 
                    <transition event='try_again' target='punching'/> 
                </state> 
            </state> 
            <state id='mode'> 
                <state id='relay'> 
                    <state id='relay_init'> 
                        <transition event='cipher_ready' target='relay_work'/> 
                    </state> 
                    <state id='relay_work'> 
                        <transition cond='In(punch_success)' target='established'/> 
                    </state> 
                </state> 
                <state id='established'> 
                </state> 
            </state> 
       </parallel> 
       <transition event='close' target='closed'/> 
       <final id='closed'>' 
       </final> 
    </scxml> 
"""


class TheMachine:
    def __init__(self):
        self.mach_ = StateMachineManager.instance().getMach("test-machine")
        self.mach_.register_state_slot('new', self.onentry_new, self.onexit_new)
        self.mach_.register_state_slot('live', self.onentry_live, self.onexit_live)
        self.mach_.register_state_slot('punch', self.onentry_punch, self.onexit_punch)
        self.mach_.register_state_slot('punching', self.onentry_punching, self.onexit_punching)
        self.mach_.register_state_slot('linked', self.onentry_linked, self.onexit_linked)
        self.mach_.register_state_slot('punch_success', self.onentry_punch_success, self.onexit_punch_success)
        self.mach_.register_state_slot('punch_fail', self.onentry_punch_fail, self.onexit_punch_fail)
        self.mach_.register_state_slot('mode', self.onentry_mode, self.onexit_mode)
        self.mach_.register_state_slot('relay', self.onentry_relay, self.onexit_relay)
        self.mach_.register_state_slot('relay_init', self.onentry_relay_init, self.onexit_relay_init)
        self.mach_.register_state_slot('relay_work', self.onentry_relay_work, self.onexit_relay_work)
        self.mach_.register_state_slot('established', self.onentry_established, self.onexit_established)
        self.mach_.register_state_slot('closed', self.onentry_closed, self.onexit_closed)
        
        self.mach_.StartEngine()
    
    
    def onentry_new(self):
        print("onentry_new")
    
    def onexit_new(self):
        print("onexit_new")
    
    def onentry_live(self):
        print("onentry_live")
    
    def onexit_live(self):
        print("onexit_live")
    
    def onentry_punch(self):
        print("onentry_punch")
    
    def onexit_punch(self):
        print("onexit_punch")
    
    def onentry_punching(self):
        print("onentry_punching")
    
    def onexit_punching(self):
        print("onexit_punching")
    
    def onentry_linked(self):
        print("onentry_linked")
    
    def onexit_linked(self):
        print("onexit_linked")
    
    def onentry_punch_success(self):
        print("onentry_punch_success")
    
    def onexit_punch_success(self):
        print("onexit_punch_success")
    
    def onentry_punch_fail(self):
        print("onentry_punch_fail")
    
    def onexit_punch_fail(self):
        print("onexit_punch_fail")
    
    def onentry_mode(self):
        print("onentry_mode")
    
    def onexit_mode(self):
        print("onexit_mode")
    
    def onentry_relay(self):
        print("onentry_relay")
    
    def onexit_relay(self):
        print("onexit_relay")
    
    def onentry_relay_init(self):
        print("onentry_relay_init")
    
    def onexit_relay_init(self):
        print("onexit_relay_init")
    
    def onentry_relay_work(self):
        print("onentry_relay_work")
    
    def onexit_relay_work(self):
        print("onexit_relay_work")
    
    def onentry_established(self):
        print("onentry_established")
    
    def onexit_established(self):
        print("onexit_established")
    
    def onentry_closed(self):
        print("onentry_closed")
    
    def onexit_closed(self):
        assert(0 and "exit final")
        print("onexit_closed")
    
    def test(self):
        self.mach_.enqueEvent("punch")
        self.mach_.enqueEvent("linked")
        self.mach_.frame_move(0)


if __name__ == '__main__':
    StateMachineManager.instance().set_scxml("test-machine", client_scxml)
    mach = TheMachine()
    mach.test ()
    StateMachineManager.instance().pumpMachEvents()
    StateMachineManager.instance().release_instance()
