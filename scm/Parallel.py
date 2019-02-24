from .State import State


done_state_prefix = "done.state."


class Parallel(State):
    
    def __init__(self, state_id, parent, machine):
        State.__init__(self, state_id, parent, machine)
        self.finished_substates_ = set()
    
    def clone(self, parent, m):
        pa = Parallel(self.state_id_, parent, m)
        pa.clone_data(self)
        return pa
    
    def makeSureEnterStates(self):
        self.enterState(True)
        for substate in self.substates_:
            substate.makeSureEnterStates()

    def onEvent(self, e):
        if self.isLeavingState():
            return
        
        if self.done_:
            return
        
        if e[0:len(done_state_prefix)] == done_state_prefix:
            state_uid = e[len(done_state_prefix):]
            if state_uid:
                self.finished_substates_.add(state_uid)
                              
        for tran in self.transitions_:
            if tran.attr_.event_ == e:
                if self.trig_cond(tran):
                    self.changeState(tran)
                    return
                
        for substate in self.substates_:
            substate.onEvent(e)
            
        if len(self.finished_substates_) == len(self.substates_):
            self.done_ = True
            self.signal_done_.emit()
            self.machine_().enqueEvent(done_state_prefix + self.state_uid_)

    
    def enterState(self, enter_substate=True):
        if self.active_:
            return
        
#        if not self.substates_:
#            raise Exception("Parallen have no substates!")
 
        if self.parent_() and self.machine_().history_type(self.parent_().state_uid()):
            self.parent_().history_state_id_ = self.state_uid_
            
        self.finished_substates_ = set()
        
        self.done_ = False
        self.active_ = True
        self.reset_time()
        
        self.machine_().current_leaf_state_ = self
        self.signal_onentry_.emit()
        
        if self.parent_() and not self.parent_().inStateObj(self, False):
            return
        
        if enter_substate:
            for substate in self.substates_:
                substate.enterState(enter_substate)
        

    def doEnterState(self, vps):
        state = vps[-1]
        if state.depth_ <= self.depth_:
            return
        
        vps.pop()
        
        for substate in self.substates_:
            if state is substate:
                state.enterState(False)
                if vps:
                    state.doEnterState(vps)
                return
        

    def exitState(self):
        if not self.active_:
            return
        
        for substate in self.substates_:
            substate.exitState()
            
        self.active_ = False
        
        self.signal_onexit_.emit()
        

    def inState(self, state_id, recursive=True):
        for substate in self.substates_:
            if substate.state_uid_ == state_id:
                return True
            
        if recursive:
            for substate in self.substates:
                if substate.inState(state_id, recursive):
                    return True
                
        return False

    
    def inStateObj(self, state, recursive=True):
        for substate in self.substates_:
            if substate is state:
                return True
            
        if recursive:
            for substate in self.substates_:
                if substate.inStateObj(state, recursive):
                    return True
                
        return False
    
    
    def onFrameMove(self, t):
        if self.isLeavingState():
            if self.check_leaving_state_finished(t):
                return
        
        for substate in self.substates_:
            substate.frame_move(t)
            if not self.active_:
                return
            
        self.pumpNoEvents()
        
        if not self.active_:
            return
        
        for slot in self.frame_move_slots_:
            slot(t)


