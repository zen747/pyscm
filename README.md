# pyscm
A python state machine framework based on statecharts (scxml).

This is a python library supporting statechart (in scxml format) originated by David Harel.
Features like hierarchical states, parallel states, and history are ready for you to command.
You won't find another lib as easy and flexible to use as SCM.

Just take a look and run scm_tutorial.py.
The code is listed here:
```
from scm import StateMachineManager


client_scxml = """\
   <scxml> 
       <state id='appear'> 
           <transition event='born' ontransit='say_hello' target='live'/> 
       </state> 
       <parallel id='live'> 
            <transition event='hp_zero' target='dead'/> 
            <state id='eat'> 
            </state> 
            <state id='move'> 
            </state> 
       </parallel> 
       <final id='dead'/>
    </scxml> 
"""

class Life:
    def __init__(self):
        self.mach_ = StateMachineManager.instance().getMach('the life')
        self.mach_.set_do_exit_state_on_destroy(True)
        self.mach_.register_state_slot("appear", self.onentry_appear, self.onexit_appear)
        self.mach_.register_state_slot("live", self.onentry_live, self.onexit_live)
        self.mach_.register_state_slot("eat", self.onentry_eat, self.onexit_eat)
        self.mach_.register_state_slot("move", self.onentry_move, self.onexit_move)
        self.mach_.register_state_slot("dead", self.onentry_dead, self.onexit_dead)
        self.mach_.register_action_slot('say_hello', self.say_hello)
        self.mach_.StartEngine()
        
    def test(self):
        self.mach_.enqueEvent("born")
        #self.mach_.frame_move(0) # state change to 'live'
        StateMachineManager.instance().pumpMachEvents()
        self.mach_.enqueEvent("hp_zero")
        #self.mach_.frame_move(0) # state change to 'dead'
        StateMachineManager.instance().pumpMachEvents()
        
    def onentry_appear(self):
        print("come to exist")
    
    def onexit_appear(self):
        print("we are going to...")
    
    def onentry_live(self):
        print("start living")
    
    def onexit_live(self):
        print("no longer live")
    
    def onentry_eat(self):
        print("start eating")
    
    def onexit_eat(self):
        print("stop eating")
    
    def onentry_move(self):
        print("start moving")
    
    def onexit_move(self):
        print("stop moving")
    
    def onentry_dead(self):
        print("end")
    
    def onexit_dead(self):
        assert (0 and "should not exit final state");
        print("no, this won't get called.")
    
    def say_hello(self):
        print("\n*** Hello, World! ***\n")
        
if __name__ == '__main__':
    StateMachineManager.instance().set_scxml("the life", client_scxml)
    life = Life()
    life.test()
    StateMachineManager.instance().pumpMachEvents()

```

The output you should see:

"""
come to exist
we are going to...

*** Hello, World! ***

start living
start eating
start moving
stop eating
stop moving
no longer live
end
"""

Simply
1. you load the scxml from external file or from a string defined in your code.
2. you connect these onentry_ onexit_, etc. slots
3. you start the engine, call the framemove in main loop.
Done.

It's that easy!

Read the tutorials at
[English] (http://zen747.blogspot.tw/2017/07/a-scm-framework-tutorial-statechart.html)

[Traditional Chinese] (http://zen747.blogspot.tw/2017/07/scm-framework.html)
