from .State import State
from .FrameMover import Signal
import gc
import weakref


class TimedEventType:
    def __init__(self, time, strEvent, cancelable):
        self.time_ = time
        self.event_ = strEvent
        self.cancelable_ = cancelable


class StateMachine(State):
    
    def __init__(self, manager):
        self.manager_ = weakref.ref(manager)
        self.slots_prepared_ = False
        self.slots_connected_ = False
        self.scxml_loaded_ = False
        self.engine_started_ = False
        self.on_event_ = False
        self.with_history_ = False
        self.current_leaf_state_ = None
        self.frame_move_slots_ = dict()
        self.cond_slots_ = dict()
        self.action_slots_ = dict()
        self.allow_nop_entry_exit_slot_ = False
        self.do_exit_state_on_destroy_ = False
        self.transition_source_state_ = self.transition_target_state_ = ''
        self.timed_events_ = []
        self.queued_events_ = []
        self.states_map_ = dict()
        self.signal_prepare_slots_ = Signal();
        self.signal_connect_cond_slots_ = Signal();
        self.signal_connect_action_slots_ = Signal();
        
        State.__init__(self, '', None, self)

        self.addState(self)
    
    
    def __del__(self):
        self.clearTimedEvents()
        self.destroy_machine(self.do_exit_state_on_destroy_)
        State.__del__(self)
        
    def set_do_exit_state_on_destroy(self, yes_no):
        self.do_exit_state_on_destroy_ = yes_no
        
    def clone(self):
        mach = StateMachine(self.manager_())
        mach.state_id_ = self.state_id_
        mach.scxml_id_ = self.scxml_id_
        mach.scxml_loaded_ = self.scxml_loaded_
        
        mach.machine_ = weakref.ref(mach)
        mach.clone_data(self)
        
        return mach
        
        
    def is_unique_id(self, state_id):
        if not self.manager_():
            print('no manager')
            return True
        else:
            return self.manager_().is_unique_id(self.scxml_id_, state_id)
    
    
    def getState(self, state_uid):
        if state_uid in self.states_map_:
            return self.states_map_[state_uid]
        else:
            return None

    
    def addState(self, state):
        if not state:
            return
        self.states_map_[state.state_uid()] = state
        
        
    def removeState(self, state):
        if not state or state is self:
            return
        if self.states_map_[state.state_uid()] is state:
            del self.states_map_[state.state_uid()]
        
        
    def inState(self, state_uid):
        if state_uid in self.states_map_:
            return self.states_map_[state_uid].active()
        else:
            return False

    def elapsed_time_of_current_state(self):
        return self.current_leaf_state_.total_elapsed_time_

    def onFrameMove(self, t):
        if not self.slots_connected_:
            return
        State.onFrameMove(self, t)
        self.pumpTimedEvents()
        while len(self.queued_events_):
            self.pumpQueuedEvents()

    def pumpQueuedEvents(self):
        queued_events = self.queued_events_
        self.queued_events_ = []
        for event in queued_events:
            self.onEvent(event)
        
    def enqueEvent(self, e):
        self.queued_events_.append(e)
        self.manager_().addToActiveMach(self)
        
        
    def onEvent(self, e):
        if not self.slots_connected_:
            raise Exception('Slots not connected yet!')
        if self.on_event_:
            self.enqueEvent(e)
            return
        #print(f'onEvent({e})')
        self.on_event_ = True
        State.onEvent(self, e)
        self.on_event_ = False


    def prepareEngine(self):
        if not self.scxml_loaded_:
            raise Exception('no scxml loaded')
        self.prepare_slots()
        self.connect_slots()
        
        
    def StartEngine(self):
        if not self.scxml_loaded_:
            raise Exception('no scxml loaded')
        if self.engine_started_:
            return
        self.prepareEngine()
        self.engine_started_ = True
        self.enterState()
        
        
    def ReStartEngine(self):
        if not self.scxml_loaded_:
            raise Exception('no scxml loaded')
        if self.engine_started_:
            self.ShutDownEngine()
        self.StartEngine()


    def engineStarted(self):
        return engine_started_
    
    
    def ShutDownEngine(self, do_exit_state):
        if do_exit_state:
            self.exitState()
        self.engine_started_ = False
        
        
    def engineReady(self):
        return self.scxml_loaded_;
    
    
    def isLeavingState(self):
        return self.getEnterState().isLeavingState()


    def re_enter_state(self):
        return self.transition_source_state_ == self.transition_target_state_
    

    def getEnterState(self):
        return self.current_leaf_state_
    
    
    def prepare_slots(self):
        if self.slots_prepared_:
            return
        
        self.slots_prepared_ = True
        self.prepareActionCondSlots()
        self.onPrepareActionCondSlots()
        self.signal_prepare_slots_.emit()


    def connect_slots(self):
        if self.slots_connected_:
            return
        
        self.slots_connected_ = True
        self.connectCondSlots()
        self.onConnectCondSlots()
        self.signal_connect_cond_slots_.emit()

        self.connectActionSlots()
        self.onConnectActionSlots()
        self.signal_connect_action_slots_.emit()


    def clear_slots(self):
        self.slots_connected_ = False
        self.action_slots_ = dict()
        self.cond_slots_ = dict()
        self.frame_move_slots_ = dict()
        self.transitions_ = []
            

    def destroy_machine(self, do_exit_state):
        if self.slots_connected_:
            if do_exit_state:
                self.exitState()
            self.scxml_loaded_ = False
        self.queued_events_ = []
        self.states_map_ = dict()
        self.machine_clear_substates()
        self.clear_slots()
        self.reset_history()
        
        self.engine_started_ = False


    def loadSCXMLString(self, xmlstr):
        if self.scxml_loaded_:
            self.destroy_machine()
        self.scxml_loaded_ = self.manager_().loadMachFromString(self, xmlstr)
        if not self.scxml_loaded_:
            self.destroy_machine()
        self.onLoadScxmlFailed()
        
        
    def GetCondSlot(self, name):
        if not self.cond_slots_:
            return None
        if name in self.cond_slots_:
            return self.cond_slots_[name]
        return None


    def GetActionSlot(self, name):
        if not self.action_slots_:
            return None
        if name in self.action_slots_:
            return self.action_slots_[name]
        return None


    def GetFrameMoveSlot(self, name):
        if not self.frame_move_slots_:
            return None
        if name in self.frame_move_slots_:
            return self.frame_move_slots_[name]
        return None
    
    
    def setCondSlot(self, name, s):
        self.cond_slots_[name] = s
        
    
    def setActionSlot(self, name, s):
        self.action_slots_[name] = s
        
        
    def setFrameMoveSlot(self, name, s):
        self.frame_move_slots_[name] = s
    

    def registerTimedEvent(self, after_t, event_e, cancelable):
        p = TimedEventType(after_t + self.total_elapsed_time_, event_e, cancelable)
        idx = 0
        for element in self.timed_events_:
            if p.time_ > element.time_:
                idx = i
                break
            idx += 1
        self.timed_events_.insert(idx, p)
        return p
        
        
    def clearTimedEvents(self):
        self.timed_events_.clear()
        
        
    def pumpTimedEvents(self):
        idx = 0
        for p in self.timed_events_:
            if p.time_ <= self.total_elapsed_time_:
                if not p.cancelable_ or len(gc.get_referrers(p)) > 1:
                    self.machine_.enqueEvent(p.event_)
                del self.timed_events_[idx]
            else:
                break
            idx += 1


    def state_id_of_history(self, history_id):
        return self.manager_().history_id_resided_state(self.scxml_id_, history_id)
    
    
    def history_type(self, state_uid):
        return self.manager_().history_type(self.scxml_id_, state_uid)
    
    
    def initial_state_of_state(self, state_uid):
        return self.manager_().initial_state_of_state(self.scxml_id_, state_uid)
    
    
    def onentry_action(self, state_uid):
        return self.manager_().onentry_action(self.scxml_id_, state_uid)
    
    
    def onexit_action(self, state_uid):
        return self.manager_().onexit_action(self.scxml_id_, state_uid)
    
    
    def frame_move_action(self, state_uid):
        return self.manager_().frame_move_action(self.scxml_id_, state_uid)
    
    
    def transition_attr(self, state_uid):
        return self.manager_().transition_attr(self.scxml_id_, state_uid)
    
    
    def num_of_states(self):
        return len(self.states_map_)
        

    def get_all_states(self):
        return self.manager_().get_all_states(self.scxml_id_)

    def manager(self):
        return self.manager_()

    def onPrepareActionCondSlots(self):
        pass
    
    def onConnectCondSlots(self):
        pass
    
    def onConnectActionSlots(self):
        pass
    
    def onLoadScxmlFailed(self):
        pass
    
    def register_state_slot(self, state, onentry, onexit):
        self.setActionSlot('onentry_'+state, onentry)
        self.setActionSlot('onexit_'+state, onexit)

    def register_action_slot(self, action, method):
        self.setActionSlot(action, method)
        
    def register_frame_move_slot(self, state, method):
        self.setFrameMoveSlot(state, method)
        
    def register_cond_slot(self, cond, method):
        self.setCondSlot(cond, method)

    def register_handler(self, handler):
        states = self.get_all_states()
        for state in states:
            s = state.replace('.', '_')
            try:
                self.setActionSlot('onentry_'+state, eval('handler.onentry_' + s))
            except:
                pass
            try:
                self.setActionSlot('onexit_'+state, eval('handler.onexit_' + s))
            except:
                pass
        
        
        
        
        
