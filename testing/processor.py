import numpy as np
import pandas as pd
from pykalman import KalmanFilter
from datetime import datetime

class Processor():
    def __init__(self):
        self.labels = ["time", "accel_x", "accel_y", "accel_z", "pitch", "roll", "yaw", "temperature", "pressure",
                  "humidity", "markers"]
        # maybe try https://docs.scipy.org/doc/numpy/reference/generated/numpy.recarray.html#numpy.recarray ?
        self.data = np.zeros((2, 11))
        self.vectors = []
        self.startTime = None
        print(self.data)

    def append_data(self, time, accel_x, accel_y, accel_z, pitch, roll, yaw, temperature, pressure, humidity, markers=0):
        dt_obj = datetime.strptime(time,
                                   '%Y-%m-%d %H:%M:%S.%f')
        time = dt_obj.timestamp()

        if self.startTime == None:
            self.startTime = time

        time -= self.startTime

        new_row = np.array([time, accel_x, accel_y, accel_z, pitch, roll, yaw, temperature, pressure, humidity])
        new_row = new_row.astype(np.float)

        # calculate vectors
        accel3D = np.linalg.norm(np.array([accel_x, accel_y, accel_z]))
        gyro3D = np.array([pitch, roll, yaw])
        new_row = np.append(new_row, accel3D)
        #new_row = np.append(new_row, gyro3D)

        self.data = np.append(self.data, np.array([new_row]), axis=0)

        if (len(self.data) < 40):
            print(new_row)
            print(self.data)
            pass

    def get_data(self):
        return self.data











