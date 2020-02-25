from communicator import Communicator
class Actuator:
    def __init__(self):
        self.communicator = Communicator()

    def actuate(self):
        print("activate")

    def retract(self):
        print("retract")