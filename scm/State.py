from .FrameMover import FrameMover, Signal, Connection
from random import randint
import weakref

class TransitionAttr:
    def __init__(self, event, target):
        self.event_ = event
        self.transition_target_ = target
        self.not_ = False   # to support "!In(state)"
        self.random_target_ = []
        self.cond_ = ''     # for later connecting slot
        self.ontransit_ = ''# for later connecting slot
        self.in_state_ = '' # for inState check if set
        

class Transition:
    def __init__(self, attr):
        self.attr_ = attr
        self.cond_functor_ = None
        self.signal_transit_ = Signal()
        
    def setAttr(self, attr):
        self.attr_ = attr
        
        
class State(FrameMover):

    done_state_prefix = "done.state."
    

    def __init__(self, state_id, parent, machine):
        FrameMover.__init__(self)
        self.parent_ = weakref.ref(parent) if parent else None
        self.machine_ = weakref.ref(machine) if machine else None
        self.substates_  = []
        self.no_event_transitions_ = []
        self.transitions_ = []
        self.frame_move_slots_ = []
        self.slots_ready_ = False
        if self.parent_:
            self.depth_ = self.parent_().depth_ + 1
        else:
            self.depth_ = 0
        self.active_ = False
        self.done_ = False
        self.is_a_final_ = False
        self.current_state_ = None
        self.history_state_id_ = ''
        self.leaving_delay_ = 0.0
        self.leaving_target_transition_ = None
        self.leaving_elapsed_seconds_ = 0.0
        self.state_id_ = ''
        self.is_unique_state_id_ = True
        self.set_state_id(state_id)
        self.signal_done_ = Signal()
        self.signal_onentry_ = Signal()
        self.signal_onexit_ = Signal()
        #print(f'new {self.state_uid_}')
    
    def __del__(self):
        #print(f'delete {self.state_uid_}')
        pass

    def set_state_id(self, state_id):
        if self.slots_ready_:
            raise Exception("slots already ready, can't change state id!")

        if self.state_id_ and self.machine_() is not self:
            self.machine_().removeState(self)
            
        self.state_id_ = state_id
        
        if not self.state_id_: # anonymous state, generate one
            if self.machine_() is self:
                self.state_id_ = '_root'
            else:
                self.state_id_ = '_st' + str(self.machine_().num_of_states())
        else:
            self.is_unique_state_id_ = self.machine_().is_unique_id(self.state_id_)
            
        if self.is_unique_state_id_:
            self.state_uid_ = self.state_id_
        else:
            self.state_uid_ = self.parent_().state_uid_ + '.' + self.state_id_
            
        if self.machine_() is not self: # delay addState to after machine_() construction complete.
            self.machine_().addState(self)
            

    def state_id(self):
        return self.state_id_
    

    def state_uid(self):
        return self.state_uid_
    

    def depth(self):
        return self.depth_
    

    def active(self):
        return self.active_
    

    def done(self):
        return self.done_
    
    
    def leavingDelay(self):
        return self.leaving_delay_


    def isLeavingState(self):
        return self.leaving_target_transition_
    
    
    def setLeavingDelay(self, delay):
        self.leaving_delay_ = delay
    

    def initial_state(self):
        initstate = self.machine_().initial_state_of_state(self.state_uid_)
        if initstate:
            return inits;
        elif self.substates_:
            return substates_[0].state_uid()
        else:
            return "" # a leaf state has no initial.
        

    def machine_clear_substates(self):
        for substate in self.substates_:
            substate.machine_clear_substates ()

        self.machine_ = None
        self.substates_ = []


    def clone(self, parent, machine):
        state = State(self.state_id_, parent, machine)
        state.clone_data(self)
        return state

    
    def clone_data(self, rhs):
        for substate in rhs.substates_:
            self.substates_.append(substate.clone(self, self.machine_()))
            
        self.depth_ = rhs.depth_
        self.is_a_final_ = rhs.is_a_final_
        self.is_unique_state_id_ = rhs.is_unique_state_id_
        self.leaving_delay_ = rhs.leaving_delay_

        
    def reset_history(self):
        if not self.machine_:
            return
        
        if self.machine_().history_type(self.state_uid_):
            self.clearHistory()
            
        for substate in self.substates_:
            substate.reset_history()


    def clearHistory(self):
        self.history_state_id_ = ''

        
    def clearDeepHistory(self):
        self.history_state_id_ = ''
        for substate in self.substates_:
            substate.clearDeepHistory()

            
    def trig_cond(self, tran):
        if tran.cond_functor_:
            change = tran.cond_functor_()
            if tran.attr_.not_:
                change = not change
            return change
        elif tran.attr_.in_state_:
            change = self.machine_().inState(tran.attr_.in_state_)
            if tran.attr_.not_:
                change = not change
            return change
        else:
            return True


    def enterState(self, enter_substate=True):
        if self.active_:
            return # already in state
        
        if self.parent_ and self.machine_().history_type(self.parent_().state_uid()):
            self.parent_().history_state_id_ = self.state_uid_
            
        self.reset_time()

        self.done_ = False
        self.active_ = True
        
        self.machine_().current_leaf_state_ = self
        self.signal_onentry_.emit()
        
        if not self.active_: # in case state changed immediately at last signal_onentry.
            return
        
        if enter_substate:
            self.doEnterSubState()
            
        if self.is_a_final_ and self.parent_():
            self.parent_().done_ = True
            self.parent_().signal_done_.emit()
            self.machine_().enqueEvent(State.done_state_prefix + self.parent_().state_uid())


    def exitState(self):
        if not self.active_:
            return
        
        if self.current_state_:
            self.current_state_.exitState()
            
        self.active_ = False
        self.current_state_ = None
        
        self.signal_onexit_.emit()

    
    def onEvent(self, e):
        if self.done_:
            return
        
        if self.isLeavingState():
            return
        
        for tran in self.transitions_:
            if tran.attr_.event_ == e:
                change = self.trig_cond(tran)
                if change:
                    self.changeState(tran)
                    return
                
        if self.current_state_:
            self.current_state_.onEvent(e)


    def findState(self, state_id, exclude=None, check_parent=True):
        for substate in self.substates_:
            if substate.state_id() == state_id:
                return substate
            
        for substate in self.substates_:
            if substate is not exclude:
                st = substate.findState(state_id, exclude, False)
                if st:
                    return st
                
        if check_parent and self.parent_():
            st = self.parent_().findState(state_id, self, True)
            if st:
                return st
            
        return None


    def changeState(self, transition):
        if transition.attr_.random_target_:
            index = randint(0, len(transition.attr_.random_target_)-1)
            target = transition.attr_.random_target_[index]
        else:
            target = transition.attr_.transition_target_
            
        corresponding_state = self.machine_().state_id_of_history(target)
        if corresponding_state:
            st = self.machine_().getState(corresponding_state)
            if st.history_state_id_:
                target = st.history_state_id_
            else:
                target = st.initial_state()
                
        self.machine_().transition_source_state_ = self.state_uid_
        self.machine_().transition_target_state_ = target
        
        #print(f"change state from '{self.state_uid_}' to '{target}'")

        if not self.leaving_target_transition_:
            if self.leaving_delay_ != 0:
                attr = TransitionAttr(transition.attr_.event_, target)
                self.leaving_target_transition_ = Transition(attr)
                self.leaving_target_transition_.setAttr(attr)
                if transition.attr_.ontransit_:
                    slot = self.machine_().GetActionSlot(transition.attr_.ontransit_)
                    if slot:
                        self.leaving_target_transition_.signal_transit_.connect(slot)
                return
                
        newState = []
        if ',' not in target:
            st = self.machine_().getState(target)
            if st:
                newState.append(st)
            else:
                raise Exception(f"can't find transition target '{target}'!")
        else:
            targets = target.split(',')
            for t in targets:
                st = self.machine_().getState(t)
                if st:
                    newState.append(st)
                else:
                    raise Exception("can't find transition target state!")

        if not newState:
            raise Exception("can't find transition target state!")

        lcaState = self.findLCA(newState[0])
        
        if not lcaState:
            raise Exception("can't find common ancestor state!")
        
        # make sure they are in the same parallel state?
        if len(newState) > 1:
            for st in newState:
                lca = self.findLCA(st)
                if lca is not lcaState:
                    raise Exception("multiple targets but have no common ancestor.");

        # exit old states
        if len(newState) == 1 and lcaState is newState[0]:
            self.machine_().transition_source_state_ = lcaState.state_uid()
            lcaState.exitState()
            transition.signal_transit_.emit()
            lcaState.enterState()
            return
        elif lcaState.current_state_:
            self.machine_().transition_source_state_ = lcaState.current_state_.state_uid()
            lcaState.current_state_.exitState()
            
        transition.signal_transit_.emit()

        # enter new state
        vps = []
        for st in newState:
            vps.append(st)
            parentstate = st.parent_()
            while parentstate and parentstate is not lcaState:
                vps.append(parentstate)
                parentstate = parentstate.parent_()
                
        lcaState.doEnterState(vps)
        lcaState.makeSureEnterStates()


    def doEnterState(self, vps):
        state = vps[-1]
        if state.depth_ <= self.depth_:
            return
        
        vps.pop()
        self.current_state_ = state
        self.current_state_.enterState(False)
        if vps:
            self.current_state_.doEnterState(vps)
        

    def doEnterSubState(self):
        if self.history_state_id_ and self.machine_().history_type(self.state_uid_):
            self.current_state_ = self.machine_().getState(self.history_state_id_)
            self.current_state_.enterState()
        else:
            if self.substates_:
                initial_state = self.machine_().initial_state_of_state(self.state_uid_)
                if not initial_state:
                    self.current_state_ = self.substates_[0]
                    self.current_state_.enterState()
                else:
                    attr = TransitionAttr('', initial_state)
                    tran = Transition(attr)
                    self.changeState(tran)


    def findLCA(self, ots):
        if not ots:
            raise Exception("findLCA on None object")
        if self is ots:
            return self
        elif self.depth_ > ots.depth_:
            return self.parent_().findLCA(ots)
        elif self.depth_ < ots.depth_:
            return self.findLCA(ots.parent_())
        else:
            if self.parent_() is ots.parent_():
                return self.parent_()
            else:
                return self.parent_().findLCA(ots.parent_())
        
        return None


    def inState(self, state_id, recursive=True):
        if not self.current_state_:
            return False
        if self.current_state_.state_id_ == state_id:
            return True
        elif recursive:
            return self.current_state_.inState(state_id, recursive)
        else:
            return False


    def inStateObj(self, state, recursive=True):
        if not self.current_state_:
            return False
        if self.current_state_ is state:
            return True
        elif recursive:
            return self.current_state_.inStateObj(state, recursive)
        else:
            return False


    def makeSureEnterStates(self):
        self.enterState(True)
        if not self.current_state_  and self.substates_:
            self.doEnterSubState()
        if self.current_state_:
            self.current_state_.makeSureEnterStates()


    def prepareActionCondSlots(self):
        if self.slots_ready_:
            return
        
        self.slots_ready_ = True
        
        tran_attrs = self.machine_().transition_attr(self.state_uid_)
        size = len(tran_attrs)
        for i in range(size):
            ptr = Transition(tran_attrs[i])
            if not tran_attrs[i].event_:
                self.no_event_transitions_.append(ptr)
            else:
                self.transitions_.append(ptr)
        
        self.machine_().setActionSlot(f'clh({self.state_uid_}*)', self.clearDeepHistory)
        self.machine_().setActionSlot(f'clh({self.state_uid_})', self.clearHistory)
        
        for substate in self.substates_:
            substate.prepareActionCondSlots()


    def connectCondSlots(self):
        self.connect_transitions_conds(self.transitions_)
        self.connect_transitions_conds(self.no_event_transitions_)
        
        for substate in self.substates_:
            substate.connectCondSlots()


    def connect_transitions_conds(self, transitions):
        """      """
        size = len(transitions)
        for i in range(size):
            if transitions[i].attr_.cond_:
                cond = transitions[i].attr_.cond_
                instate_check = cond[0:3]
                if instate_check == "In(" or instate_check == "in(":
                    endmark = cond.find(')', 4)
                    st = cond[3:endmark]
                    if not self.machine_().is_unique_id(st):
                        s = self.findState(st)
                        if not s:
                            raise Exception("can't find state for In() check")
                        st = s.state_uid()
                    transitions[i].attr_.in_state_ = st
                else:
                    s = self.machine_().GetCondSlot(cond)
                    if s:
                        transitions[i].cond_functor_ = s
                    else:
                        raise Exception("can't connect cond slot")
        

    def connectActionSlots(self):
        onentry = self.machine_().onentry_action(self.state_uid_)
        if onentry:
            s = self.machine_().GetActionSlot(onentry)
            if s:
                self.signal_onentry_.connect(s)
            elif onentry != f'onentry_{self.state_uid_}':
                raise Exception("can't connect onentry slot")

        onexit = self.machine_().onexit_action(self.state_uid_)
        if onexit:
            s = self.machine_().GetActionSlot(onexit)
            if s:
                self.signal_onexit_.connect(s)
            elif onexit != f'onexit_{self.state_uid_}':
                raise Exception("Can't connect onexit slot")
            
        frame_move = self.machine_().frame_move_action(self.state_uid_)
        if frame_move:
            sf = self.machine_().GetFrameMoveSlot(frame_move)
            if sf:
                self.frame_move_slots_.append(sf)
            elif frame_move != self.state_uid_:
                raise Exception("Can't connect frame_move slot")
            
        self.connect_transitions_signal(self.transitions_)
        self.connect_transitions_signal(self.no_event_transitions_)
        
        for substate in self.substates_:
            substate.connectActionSlots()


    def connect_transitions_signal(self, transitions):
        for tran in transitions:
            if tran.attr_.ontransit_:
                tr = tran.attr_.ontransit_
                s = self.machine_().GetActionSlot(tr)
                if s:
                    tran.signal_transit_.connect(s)
                else:
                    raise Exception("can't connect on_transit slot")
                

    def doLeaveAferDelay(self):
        if self.leaving_target_transition_:
            self.changeState(self.leaving_target_transition_)
            self.leaving_target_transition_ = None
            self.leaving_elapsed_seconds_ = 0

    def check_leaving_state_finished(self, t):
        if self.leaving_delay_ < 0:
            return False
        self.leaving_elapsed_seconds_ += t
        if self.leaving_elapsed_seconds_ >= self.leaving_delay_:
            self.doLeaveAferDelay()
            return True
        return False
        

    def onFrameMove(self, t):
        if self.isLeavingState():
            if self.check_leaving_state_finished(t):
                return
            
        if self.current_state_:
            self.current_state_.frame_move(t)
            if not self.active_:
                return 
    
        self.pumpNoEvents()
        
        if not self.active_:
            return
        
        for slot in self.frame_move_slots_:
            slot(t)
            
            
    def pumpNoEvents(self):
        for tran in self.no_event_transitions_:
            if self.trig_cond(tran):
                self.changeState(tran)
                return

