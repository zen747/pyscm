from scm import StateMachineManager



cm_scxml = """
   <scxml> 
        <state id="idle"> 
            <transition event="empty" target="disabled"/> 
            <transition event="coin" target="active"/> 
        </state> 
        <state id="active"> 
            <transition event="release-candy" ontransit="releaseCandy" target="releasing"/> 
            <transition event="withdraw-coin" ontransit="withdrawCoins" target="idle"/> 
        </state> 
        <state id="releasing"> 
            <transition event="candy-released" cond="condNoCandy" target="disabled"/> 
            <transition event="candy-released" target="idle"/> 
        </state> 
        <state id="disabled"> 
            <transition event="add-candy" cond="condNoCredit" target="idle"/> 
            <transition event="add-candy" target="active"/> 
        </state> 
    </scxml> 
"""


class TheCandyMachine:
    def __init__(self):
        self.credit_ = 0
        self.num_of_candy_stored_ = 0
        mach = self.mach_ = StateMachineManager.instance().getMach("cm_scxml")
        mach.register_state_slot('idle', self.onentry_idle, self.onexit_idle)
        mach.register_state_slot('active', self.onentry_active, self.onexit_active)
        mach.register_state_slot('releasing', self.onentry_releasing, self.onexit_releasing)
        mach.register_state_slot('disabled', self.onentry_disabled, self.onexit_disabled)

        mach.register_cond_slot('condNoCandy', self.condNoCandy)
        mach.register_cond_slot('condNoCredit', self.condNoCredit)
        
        mach.register_action_slot('releaseCandy', self.releaseCandy)
        mach.register_action_slot('withdrawCoins', self.withdrawCoins)
        
        mach.StartEngine()
    
    def __del__(self):
        self.mach_.ShutDownEngine(True)
        
    
    def store_candy(self, num):
        self.num_of_candy_stored_ += num
        self.mach_.enqueEvent("add-candy")
        print(f"store {num} gumballs, now machine has {self.num_of_candy_stored_:.0f} gumballs.")
    
    def insertQuater(self):
        self.insert_coin(25)
        print(f"you insert a quarter, now credit = {self.credit_:.0f}")
    
    def ejectQuater(self):
        self.mach_.enqueEvent("withdraw-coin")
        print("you pulled the eject crank")
    
    def turnCrank(self):
        self.mach_.enqueEvent("release-candy")
        print("you turned release crank")
    

    def insert_coin(self, credit):
        self.credit_ += credit
        self.mach_.enqueEvent("coin")
        
    def onentry_idle(self):
        print("onentry_idle")
        print("Machine is waiting for quarter")
        if self.num_of_candy_stored_ == 0:
            self.mach_.enqueEvent ("empty")
    
    def onexit_idle(self):
        print("onexit_idle")
    
    def onentry_active(self):
        print("onentry_active")
    
    def onexit_active(self):
        print("onexit_active")
    
    def onentry_releasing(self):
        print("onentry_releasing")
        #PunctualFrameMover::registerTimedAction(1.0, boost::bind(&TheCandyMachine::candy_released, this))
        self.candy_released()
    
    def onexit_releasing(self):
        print("onexit_releasing")
    
    def onentry_disabled(self):
        print("onentry_disabled")
    
    def onexit_disabled(self):
        print("onexit_disabled")
    
    def condNoCandy(self):
        return self.num_of_candy_stored_ == 0
    
    def condNoCredit(self):
        return self.credit_ == 0
    
    def releaseCandy(self):
        num_to_release = self.credit_ / 25
        if num_to_release > self.num_of_candy_stored_:
            num_to_release = self.num_of_candy_stored_

        print(f"release {num_to_release:.0f} gumballs")
        self.num_of_candy_stored_ -= num_to_release
        self.credit_ -= num_to_release * 25
    
    def withdrawCoins(self):
        print(f"there you go, the money, {self.credit_:.0f}")
        self.credit_ = 0
        print("Quarter returned")
    
    def candy_released(self):
        self.mach_.enqueEvent("candy-released")
    
    
    def report(self):
        print("\nA Candy Selling Machine")
        print(f"Inventory: {self.num_of_candy_stored_:.0f} gumballs")
        print(f"Credit: {self.credit_:.0f}\n")
    
    def init(self):
        self.mach_.frame_move(0)
        assert (self.mach_.inState("disabled"))
        self.store_candy(5)
        self.mach_.frame_move(0)
        assert (self.mach_.inState("idle"))
        self.report()       
    
    def frame_move(self):
        self.mach_.frame_move(0)
    
    def test(self):
        self.insertQuater()
        self.frame_move()
        self.turnCrank()
        self.frame_move()
        self.report ()
        
        self.insertQuater()
        self.frame_move()
        self.ejectQuater()
        self.frame_move()
        self.report ()
        self.turnCrank()
        self.frame_move()
        self.report ()
        
        self.insertQuater()
        self.frame_move()
        self.turnCrank()
        self.frame_move()
        self.insertQuater()
        self.frame_move()
        self.turnCrank()
        self.frame_move()
        self.ejectQuater()
        self.frame_move()
        self.report()

        self.insertQuater()
        self.frame_move()
        self.insertQuater()
        self.frame_move()
        self.turnCrank()
        self.frame_move()
        self.insertQuater()
        self.frame_move()
        self.turnCrank()
        self.frame_move()
        self.insertQuater()
        self.frame_move()
        self.ejectQuater()
        self.frame_move()
        self.report()

        self.store_candy(5)
        self.frame_move()
        self.turnCrank()
        self.frame_move()        
        self.report()


def test():
    mach = TheCandyMachine()
    mach.init ()
    mach.test ()
    
if __name__ == '__main__':
    
    StateMachineManager.instance().set_scxml("cm_scxml", cm_scxml)
#    StateMachineManager::instance().set_scxml_file("cm_scxml", "cm.scxml") // optionally through a file
#    StateMachineManager::instance().prepare_machs() // optionally load all scxml at once or getMach() on the fly
    
    test()
    
    StateMachineManager.instance().pumpMachEvents()
    #StateMachineManager.instance().release_instance()
