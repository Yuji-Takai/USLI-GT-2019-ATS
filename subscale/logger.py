from sense_hat import SenseHat
from datetime import datetime
import time
import os
import RPi.GPIO as GPIO
import serial

class SensorData():
    def __init__(self, timestamp, accel, gyro, temp, p, humidity):
        self.timestamp = timestamp
        self.accel = accel
        self.gyro = gyro
        self.temp = temp
        self.p = p
        self.humidity = humidity


class Logger():
    def __init__(self):
        self.log_directory = "/home/pi/sensehat_test/data"
        self.shutdown_armed = True
        self.sense = SenseHat()
        today = datetime.today()
        self.log_fname = "{}_{}_{}_{}:{}.csv".format(today.year, today.month, today.day, today.hour, today.minute)
        self.port = serial.Serial("/dev/ttyAMA0")
        #Setting up the GPIO Pins
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        #Set baud rate to 9600
        self.port.baudrate = 9600 
        self.start = None
        self.launched = False
        self.activated = False
        self.locked = False

    def log(self):
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
        os.chdir(self.log_directory)
        # initialize log file
        with open(self.log_fname, 'w') as f:
            f.write("{},{},{},{},{},{},{},{},{},{}\n".format("time", "accel_x",
                "accel_y", "accel_z", "pitch", "roll", "yaw", "temperature",
                "pressure", "humidity"))
        sense_data = []
        counter = 0
        red = (255, 0, 0)
        green = (0, 255, 0)
        blue = (0, 0, 255)
        self.sense.show_message("OK", text_colour=green)
        while True:
            acceler = self.sense.get_accelerometer_raw()
            sense_data.append(SensorData(datetime.now(), acceler,
                self.sense.get_orientation(), self.sense.get_temperature(),
                self.sense.get_pressure(),
                self.sense.get_humidity()))
            counter += 1
            if counter % 10 == 0:
                self.write_csv(sense_data)
                sense_data = []
            if counter % 500 == 0:
                self.port.write("GOOD\n")
                print("GOOD")

            # If the acceleration is more than 5G (less -5G b/c of the
            # orientation), determine that the rocket was launched
            if not self.launched and acceler['x'] <= -5:
                self.launched = True

            # If the rocket was launched and the acceleration is negative G
            # and there is no activation made yet, activate the mechanism
            # activated is turned on
            if self.launched and acceler['x'] > 0 and not self.activated and not self.locked:
                self.activated = True
                self.start = time.time()
                self.activate()

            if self.activated and counter % 10 == 0:
                self.activate()

            if self.activated and time.time() - self.start >= 60:
                # set locked true to no longer call activated (stops sending command to Arduino)
                self.locked = True
                # set activated false to not call activate anymore once in 10 cycles
                self.activated = False

            if self.shutdown_armed:
                for event in self.sense.stick.get_events():
                    print("The joystick was {} {}".format(event.action, event.direction))
                    if (event.direction == "down" and event.action == "pressed"):
                        self.sense.show_message("shutdown", text_colour=red)
                        os.system("sudo shutdown -hP now")
                    if (event.direction == "middle" and event.action == "pressed"):
                        self.shutdown_armed = False
                        self.sense.show_message("shutdown disarmed", text_colour=green)

    def write_csv(self, sense_data):
        with open(self.log_fname, 'a') as f:
            for data in sense_data:
                f.write("{},{},{},{},{},{},{},{},{},{}\n".format(data.timestamp,
                    data.accel['x'], data.accel['y'], data.accel['z'],
                    data.gyro['pitch'], data.gyro['roll'], data.gyro['yaw'],
                    data.temp, data.p, data.humidity))

    def activate(self):
        self.port.write("MOVE\n")



def main():
    """
    main function that obtains data from Sense HAT and logs data to file
    """
    logger = Logger()
    logger.log()

if __name__ == '__main__':
    main()
