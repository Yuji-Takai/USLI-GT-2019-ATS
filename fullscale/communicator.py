# import RPi.GPIO as GPIO
# import serial

class Communicator:
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