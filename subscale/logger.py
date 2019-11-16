from sense_hat import SenseHat
from datetime import datetime
import os

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

    def log(self):
        try:
            os.makedirs(self.log_directory)
        except FileExistsError:
           # directory already exists
           pass
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
            sense_data.append(SensorData(datetime.now(), self.sense.get_accelerometer_raw(),
                self.sense.get_orientation(), self.sense.get_temperature(), self.sense.get_pressure(),
                self.sense.get_humidity()))
            counter += 1
            if counter % 10 == 0:
                self.write_csv(sense_data)
                sense_data = []
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

def main():
    """
    main function that obtains data from Sense HAT and logs data to file
    """
    logger = Logger()
    logger.log()

if __name__ == '__main__':
    main()
