from math import sqrt
from event import Event
class SensorData():
    '''
    Represents the sensor data retreived from Sense HAT
    '''
    def __init__(self, time, ax, ay, az, pitch, roll, yaw, temp, pressure, event = Event.DEFAULT):
        self.time = time
        self.ax = ax
        self.ay = ay
        self.az = az
        self.pitch = pitch
        self.roll = roll
        self.yaw = yaw
        self.temp = temp
        self.pressure = pressure
        self.event = event

    def __str__(self):
        return "{},{},{},{},{},{},{},{},{},{}".format(self.time, self.ax, self.ay,
            self.az, self.pitch, self.roll, self.yaw, self.temp, self.pressure,
            (self.event if self.event != Event.DEFAULT else ""))

    def total_accel(self):
        '''
        returns the magnitude of the acceleration of the launch vehicle
        '''
        return sqrt(self.ax ** 2 + self.ay ** 2 + self.az ** 2)

    def normalize(self, origin_time):
        '''
        normalize the time of the sensor data to the start time of the launch
        '''
        time_change = self.time - origin_time
        self.time = time_change.days * 3600 + time_change.seconds + time_change.microseconds / 1000000.0

    def subtract(self, other):
        self.ax -= other.ax
        self.ay -= other.ay
        self.az -= other.az
        self.pitch -= other.pitch
        self.roll -= other.roll
        self.yaw -= other.yaw
        self.temp -= other.temp
        self.pressure -= other.pressure

    def add(self, other):
        self.ax += other.ax
        self.ay += other.ay
        self.az += other.az
        self.pitch += other.pitch
        self.roll += other.roll
        self.yaw += other.yaw
        self.temp += other.temp
        self.pressure += other.pressure