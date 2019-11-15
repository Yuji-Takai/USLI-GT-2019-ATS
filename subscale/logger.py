from sense_hat import SenseHat
from datetime import datetime

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
        self.sense = SenseHat()
        today = datetime.today()
        self.log_fname = "{}_{}_{}_{}:{}.csv".format(today.year, today.month, today.day, today.hour, today.minute)

    def log(self):
        # initialize log file
        with open(self.log_fname, 'w') as f:
            f.write("{},{},{},{},{},{},{},{},{},{}\n".format("time", "accel_x",
                "accel_y", "accel_z", "pitch", "roll", "yaw", "temperature",
                "pressure", "humidity"))
        sense_data = []
        counter = 0
        while counter <= 100:
            sense_data.append(SensorData(datetime.now(), self.sense.get_accelerometer_raw(),
                self.sense.get_orientation(), self.sense.get_temperature(), self.sense.get_pressure(),
                self.sense.get_humidity()))
            counter += 1
            if counter % 10 == 0:
                self.write_csv(sense_data)
                sense_data = []

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
