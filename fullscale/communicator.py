# Uncomment the imports when running on Raspberry PI
# import RPi.GPIO as GPIO
# import serial

class Communicator:
    '''
    Represents the communicator
    The class is responsible for handling the communication between the Raspberry Pi and Arduino
    '''
    def __init__(self):
        # Uncomment when running on Raspberry Pi
        self.port = serial.Serial("/dev/ttyAMA0")
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        self.port.baudrate = 9600
        self.status = "ALIVE"

    def send(self, msg):
        # Uncomment when running on Raspberry Pi 
        self.port.write("{}\n".format(msg))
        print(msg)