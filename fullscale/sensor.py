from sense_hat import SenseHat
from sensor_data import SensorData
from datetime import datetime
import time

class Sensor:
    '''
    Class responsible for getting raw sensor data from Sense HAT
    sense: SenseHat
        instance of Sense HAT
    isTest: boolean
        True if this is a test
    '''
    def __init__(self, isTest):
        self.sense = SenseHat()
        self.isTest = isTest

    def getData(self):
        '''
        returns the most recent data from Sense HAT
        '''
        accel = self.sense.get_accelerometer_raw()
        gyro = self.sense.get_orientation()
        temp = self.sense.get_temperature()
        pressure = self.sense.get_pressure()
        if self.isTest:
            time.sleep(0.01)
        return SensorData(datetime.now(), accel['x'], accel['y'], accel['z'],
            gyro['pitch'], gyro['roll'], gyro['yaw'], temp, pressure)
