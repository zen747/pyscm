from .StateMachine import StateMachine
from .State import State, TransitionAttr
from .Parallel import Parallel
import xml.etree.ElementTree as etree
import json

class ParseStruct:
    def __init__(self):
        self.current_state_ = 0
        self.machine_ = 0
        self.scxml_id_ = ''


class StateMachineManager:
    def __init__(self):
        self.mach_map_ = dict()
        self.scxml_map_ = dict()
        self.onentry_action_map_ = dict()
        self.onexit_action_map_ = dict()
        self.frame_move_action_map_ = dict()
        self.initial_state_map_ = dict()
        self.history_type_map_ = dict()
        self.history_id_reside_state_ = dict()
        self.transition_attr_map_ = dict()
        self.state_uids_ = dict()
        self.non_unique_ids_ = dict()
        self.active_machs_ = []
        
    def getMach(self, scxml_id):
        if scxml_id in self.mach_map_:
            return self.mach_map_[scxml_id].clone()
        else:
            mach = StateMachine(self)
            self.mach_map_[scxml_id] = mach
            mach.scxml_id_ = scxml_id
            if scxml_id in self.scxml_map_:
                if self.scxml_map_[scxml_id].startswith('file:'):
                    mach.scxml_loaded_ = self.loadMachFromFile(mach, self.scxml_map_[scxml_id][5:])
                else:
                    mach.scxml_loaded_ = self.loadMachFromString(mach, self.scxml_map_[scxml_id])
            return mach.clone()

    def addToActiveMach(self, mach):
        if not mach:
            raise Exception('mach None?')
        self.active_machs_.append(mach)
        
    def pumpMachEvents(self):
        while self.active_machs_:
            machs = self.active_machs_
            self.active_machs_ = []
            for mach in machs:
                mach.pumpQueuedEvents()

    def set_scxml(self, scxml_id, scxml_str):
        self.scxml_map_[scxml_id] = scxml_str
        
    def set_scxml_file(self, scxml_id, scxml_filepath):
        self.scxml_map_[scxml_id] = 'file:' + scxml_filepath
        
    def prepare_machs(self):
        for scxml_id in self.scxml_map_:
            mach = None
            if scxml_id in self.mach_map_:
                mach = self.mach_map_[scxml_id]
            else:
                mach = StateMachine(self)
                mach.scxml_id_ = scxml_id
                self.mach_map_[scxml_id] = mach
            if not mach.scxml_loaded_:
                if self.scxml_map_[scxml_id].startswith('file:'):
                    mach.scxml_loaded_ = self.loadMachFromFile(mach, self.scxml_map_[scxml_id][5:])
                else:
                    mach.scxml_loaded_ = self.loadMachFromString(mach, self.scxml_map_[scxml_id])
                
    def loadMachFromFile(self, mach, scxml_file):
        with open(scxml_file, 'r') as f:
            self.loadMachFromString(mach, f.read())
            
    def loadMachFromString(self, mach, scxml_str):
        parset_data = ParseStruct()
        parset_data.scxml_id_ = scxml_id = mach.scxml_id_
        parset_data.machine_ = mach
        parset_data.current_state_ = mach
        self.transition_attr_map_[scxml_id] = dict()
        self.state_uids_[scxml_id] = []
        self.non_unique_ids_[scxml_id] = []
        self.onentry_action_map_[scxml_id] = dict()
        self.onexit_action_map_[scxml_id] = dict()
        self.frame_move_action_map_[scxml_id] = dict()
        self.initial_state_map_[scxml_id] = dict()
        self.history_type_map_[scxml_id] = dict()
        self.history_id_reside_state_[scxml_id] = dict()
        
        return self.parse_scm_tree(parset_data, scxml_str)
        
    def clearMachMap(self):
        self.mach_map_.clear()
        self.onentry_action_map_.clear()
        self.onexit_action_map_.clear()
        self.frame_move_action_map_.clear()
        self.initial_state_map_.clear()
        self.history_type_map_.clear()
        self.history_id_reside_state_.clear()
        self.transition_attr_map_.clear()
        
    def history_id_resided_state(self, scxml_id, history_id):
        try:
            return self.history_id_reside_state_[scxml_id][history_id]
        except KeyError:
            return ''
    
    def history_type(self, scxml_id, state_uid):
        try:
            return self.history_type_map_[scxml_id][state_uid]
        except KeyError:
            return ''
        
    def initial_state_of_state(self, scxml_id, state_uid):
        try:
            return self.initial_state_map_[scxml_id][state_uid]
        except KeyError:
            return ''
        
    def onentry_action(self, scxml_id, state_uid):
        try:
            return self.onentry_action_map_[scxml_id][state_uid]
        except KeyError:
            return ''

    def onexit_action(self, scxml_id, state_uid):
        try:
            return self.onexit_action_map_[scxml_id][state_uid]
        except KeyError:
            return ''
    
    def frame_move_action(self, scxml_id, state_uid):
        try:
            return self.frame_move_action_map_[scxml_id][state_uid]
        except KeyError:
            return ''
    
    def transition_attr(self, scxml_id, state_uid):
        try:
            return self.transition_attr_map_[scxml_id][state_uid]
        except KeyError:
            return []
    
    def num_of_states(self, scxml_id):
        return len(self.state_uids_[scxml_id])
    
    def is_unique_id(self, scxml_id, state_uid):
        return state_uid not in self.non_unique_ids_[scxml_id]
    
    def get_all_states(self, scxml_id):
        return self.state_uids_[scxml_id]
        
    def parse_scm_tree (self, data, scm_str):
        scm_str = scm_str.strip()
        try:
            if scm_str[0] == '<':
                self.parse_from_xml(scm_str, data)
            else:
                scm_str = scm_str.replace("'", '"')
                self.parse_from_json(scm_str, data)
        except:
            print('parse scxml failed!')
            raise
            #return False
        
        return True
        
    def parse_from_json(self, scm_str, data):
        'todo: add json support'
        pass
        
    def parse_from_xml(self, scm_str, data):
        root = etree.fromstring(scm_str)
        self.parse_element_xml(data, root, 0)
            
    def validate_state_id(self, stateid):
        if stateid and stateid.startswith('_'):
            raise Exception("state id can't start with '_', which is reserved for internal use.")
        
    def parse_element_xml(self, data, element, level):
        manager = data.machine_.manager()
        scxml_id = data.scxml_id_

        if element.tag == 'scxml':
            manager.state_uids_[scxml_id].append(scxml_id)
            if 'non-unique' in element.attrib:
                non_unique_ids = element.attrib['non-unique'].split(',')
                manager.non_unique_ids_[scxml_id] += non_unique_ids
            
        elif element.tag == 'state':
            stateid = element.attrib['id'] if 'id' in element.attrib else ''
            self.validate_state_id(stateid)
            state = State(stateid, data.current_state_, data.machine_)
            data.current_state_.substates_.append(state)
            data.current_state_ = state
            manager.state_uids_[scxml_id].append(state.state_uid())
            self.handle_state_item(data, element.attrib)
        elif element.tag == 'parallel':
            stateid = element.attrib['id'] if 'id' in element.attrib else ''
            self.validate_state_id(stateid)
            state = Parallel(stateid, data.current_state_, data.machine_)
            data.current_state_.substates_.append(state)
            data.current_state_ = state
            manager.state_uids_[scxml_id].append(state.state_uid())
            self.handle_state_item(data, element.attrib)
        elif element.tag == 'final':
            stateid = element.attrib['id'] if 'id' in element.attrib else ''
            self.validate_state_id(stateid)
            state = State(stateid, data.current_state_, data.machine_)
            data.current_state_.substates_.append(state)
            data.current_state_ = state
            manager.state_uids_[scxml_id].append(state.state_uid())
            self.handle_final_item(data, element.attrib)
        elif element.tag == 'history':
            self.handle_history_item(data, element.attrib)
        elif element.tag == 'transition':
            self.handle_transition_item(data, element.attrib)
            
        for child in element:
            self.parse_element_xml(data, child, level+1)
            
        if element.tag == 'scxml':
            self.finish_scxml(data, element.attrib)
            #data.current_state_ = data.current_state_.parent_()
        elif element.tag == 'state':
            data.current_state_ = data.current_state_.parent_()
        elif element.tag == 'parallel':
            data.current_state_ = data.current_state_.parent_()
        elif element.tag == 'final':
            data.current_state_ = data.current_state_.parent_()
    
    
    @classmethod
    def finish_scxml(self, data, attrib):
        manager = data.machine_.manager()
        scxml_id = data.scxml_id_

        if 'initial' in attrib:
            manager.initial_state_map_[scxml_id][data.current_state_.state_uid()] = attrib['initial']
            
        # process multiple targets transition. 
        # replace non-unique target to unique id
        transition_map = manager.transition_attr_map_[scxml_id]
        for state_uid,transitions in transition_map.items():
            st = data.machine_.getState(state_uid)
            for transition in transitions:
                target_str = transition.transition_target_
                if ',' not in target_str and data.machine_.is_unique_id(target_str):
                    continue
                tstates = []
                targets = target_str.split(',')
                for i in range(len(targets)):
                    if not data.machine_.is_unique_id(targets[i]):
                        s = st.findState(targets[i])
                        assert(s and "can't find transition target, not state id?")
                        targets[i] = s.state_uid()
                    tstates.append(data.machine_.getState(targets[i]))
                transition.transition_target_ = ','.join(targets)
                
                # transition to multiple targets only apply to parallel states.
                for i in range(len(tstates)-1):
                    lca = tstates[0].findLCA(tstates[i+1])
                    assert(isinstance(lca, Parallel) and "multiple targets but can't find common ancestor.")

    @classmethod
    def handle_state_item(self, data, attributes):
        manager = data.machine_.manager()
        scxml_id = data.scxml_id_
        
        onentry = ''
        onexit = ''
        framemove = ''
        history_type = ''
        leaving_delay = 0
        
        for key,value in attributes.items():
            if key == 'id':
                pass
            elif key == 'initial':
                manager.initial_state_map_[scxml_id][data.current_state_.state_uid()] = value
            elif key == 'history':
                history_type = value
            elif key == 'onentry':
                onentry = value
            elif key == 'onexit':
                onexit = value
            elif key == 'frame_move':
                framemove = value
            elif key == 'leaving_delay':
                leaving_delay = float(value)
            else:
                print(f'attribute "{key}" not supported')
                assert (0 and f'attribute "{key}" not supported')
                
        state_uid = data.current_state_.state_uid()
        if leaving_delay: data.current_state_.setLeavingDelay(leaving_delay)
        if not onentry: onentry = "onentry_" + state_uid
        if not onexit: onexit = "onexit_" + state_uid
        if not framemove: framemove = state_uid
        
        if data.current_state_.parent_().state_uid() in manager.history_type_map_[scxml_id] and manager.history_type_map_[scxml_id][data.current_state_.parent_().state_uid()] == 'deep':
            manager.history_type_map_[scxml_id][state_uid] = "deep"
        else:
            manager.history_type_map_[scxml_id][state_uid] = history_type
            
        if not manager.history_type_map_[scxml_id][state_uid]:
            data.machine_.with_history_ = True
            
        manager.onentry_action_map_[scxml_id][state_uid] = onentry
        manager.onexit_action_map_[scxml_id][state_uid] = onexit
        manager.frame_move_action_map_[scxml_id][state_uid] = framemove


    @classmethod
    def handle_final_item(self, data, attributes):
        manager = data.machine_.manager()
        scxml_id = data.scxml_id_
        state_uid = data.current_state_.state_uid()
        onentry = ''
        onexit = ''
        framemove = ''

        for key,value in attributes.items():
            if key == 'id':
                pass
            elif key == 'onentry':
                onentry = value
            elif key == 'frame_move':
                framemove = value
            else:
                assert (0 and f'attribute "key" not supported in "final" state')
        
        if not onentry: onentry = "onentry_" + state_uid
        if not framemove: framemove = state_uid
        
        manager.onentry_action_map_[scxml_id][state_uid] = onentry
        manager.frame_move_action_map_[scxml_id][state_uid] = framemove
        
        data.current_state_.is_a_final_ = True
        
    @classmethod
    def handle_transition_item(self, data, attributes):
        manager = data.machine_.manager()
        scxml_id = data.scxml_id_
        state_uid = data.current_state_.state_uid()

        tran = TransitionAttr('','')

        for key, value in attributes.items():
            if key == 'event':
                tran.event_ = value
            elif key == 'cond':
                tran.cond_ = value
            elif key == 'ontransit':
                tran.ontransit_ = value
            elif key == 'target':
                tran.transition_target_ = value
            elif key == 'random_target':
                tran.random_target_ = value.split(',')

        if tran.cond_ and tran.cond_.startswith('!'):
            tran.cond_ = tran.cond_[1:]
            tran.not_ = True
            
        if state_uid not in manager.transition_attr_map_[scxml_id]:
            manager.transition_attr_map_[scxml_id][state_uid] = []
        manager.transition_attr_map_[scxml_id][state_uid].append(tran)
        
        
    @classmethod
    def handle_history_item(self, data, attributes):
        manager = data.machine_.manager()
        scxml_id = data.scxml_id_
        state_uid = data.current_state_.state_uid()
    
        for key, value in attributes.items():
            if key == 'type':
                manager.history_type_map_[scxml_id][state_uid] = value
            elif key == 'id':
                manager.history_id_reside_state_[scxml_id][value] = state_uid
    
    instance_ = None
    
    @classmethod
    def instance(self):
        if not self.instance_:
            self.instance_ = StateMachineManager()
        return self.instance_

    @classmethod
    def release_instance(self):
        self.instance_ = None









