from communicator import Communicator
class Actuator:
    '''
    Represents the actuator 
    '''
    def __init__(self):
        self.communicator = Communicator()

    def actuate(self):
        print("activate")

    def retract(self):
        print("retract")