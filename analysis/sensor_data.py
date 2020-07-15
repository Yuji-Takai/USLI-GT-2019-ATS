from math import sqrt
from event import Event
class SensorData():
    '''
    Represents the sensor data retreived from Sense HAT
    '''
    def __init__(self, time, ax, ay, az, pitch, roll, yaw, temp, pressure, event = Event.DEFAULT, command = ""):
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
        self.command = command

    def __str__(self):
        return "{},{},{},{},{},{},{},{},{},{},{}".format(self.time, self.ax, self.ay,
            self.az, self.pitch, self.roll, self.yaw, self.temp, self.pressure,
            (self.event if self.event != Event.DEFAULT else ""), self.command)

    def total_accel(self):
        '''
        returns the magnitude of the acceleration of the launch vehicle
        '''
        return sqrt(self.ax ** 2 + self.ay ** 2 + self.az ** 2)
