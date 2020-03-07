from communicator import Communicator
class Actuator:
    '''
    Represents the actuator 
    '''
    def __init__(self):
        self.communicator = Communicator()

    def actuate(self):
        self.communicator.send("ACT")
        print("ACT")

    def retract(self):
        self.communicator.send("RET")
        print("RET")