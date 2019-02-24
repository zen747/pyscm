


class Signal:
    "Google signals and slots to learn the concept."
    def __init__(self):
        self.slots_ = []
    
    def connect(self, func):
        self.slots_.append(func)
        return Connection(self, func)
    
    def disconnect(self, func):
        self.slots_.remove(func)
        
    def emit(self):
        for func in self.slots_:
            func()
            
class Connection:
    "The purpose of this class is to avoid the need to keep track of the origin of func"
    def __init__(self, signal, func):
        self.signal_ = signal
        self.func_ = func
        
    def disconnect(self):
        self.signal_.disconnect(self.func_)

class FrameMover:
    def __init__(self):
        self.pause_ = False
        self.total_elapsed_time_ = 0
        self.signal_on_frame_move_ = Signal()
        self.signal_on_pause_ = Signal()
        self.signal_on_resume_ = Signal()
        
    def onFrameMove(self, t):
        pass
    
    def onPause(self):
        pass
    
    def onResume(self):
        pass
    
    def connect_signal_on_frame_move(self, slot):
        return self.signal_on_frame_move_.connect(slot)
    
    def connect_signal_on_pause(self, slot):
        return self.signal_on_pause_.connect(slot)
    
    def connect_signal_on_resume(self, slot):
        return self.signal_on_resume_.connect(slot)
        
    def frame_move(self, t):
        self.total_elapsed_time_ += t
        self.signal_on_frame_move_.emit()
        self.onFrameMove(t)
        
    def pause(self):
        if not self.pause_:
            self.pause_ = True
            self.signal_on_pause_.emit()
            self.onPause()
    
    def resume(self):
        if self.pause_:
            self.pause_ = False
            self.signal_on_resume_.emit()
            self.onResume()
            
    def toggle_pause(self):
        if self.pause_:
            self.resume()
        else:
            self.pause()
    
    def is_paused(self):
        return self.pause_
    
    def total_elapsed_time(self):
        return self.total_elapsed_time_
    
    def reset_time(self):
        self.total_elapsed_time_ = 0
