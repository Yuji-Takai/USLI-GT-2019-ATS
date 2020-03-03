# import RPi.GPIO as GPIO
# import serial

class Communicator:
    '''
    Represents the communicator
    The class is responsible for handling the communication between the Raspberry Pi and Arduino
    '''
    def __init__(self):
        # self.port = serial.Serial("/dev/ttyAMA0")
        # #Setting up the GPIO Pins
        # GPIO.setwarnings(False)
        # GPIO.setmode(GPIO.BCM)
        # GPIO.cleanup()
        # #Set baud rate to 9600
        # self.port.baudrate = 9600
        self.status = "ALIVE"

    def send(self, msg):
        # self.port.write("{}\n".format(msg))
        print(msg)