import numpy as np
import pandas as pd
from pykalman import KalmanFilter
from datetime import datetime
import pvlib.atmosphere

class Processor():
    def __init__(self):
        self.labels = ["time", "accel_x", "accel_y", "accel_z", "pitch", "roll", "yaw", "temperature", "pressure",
                  "humidity", "accel_mag", "altitude"]
        print(self.labels.index("time"))
        # maybe try https://docs.scipy.org/doc/numpy/reference/generated/numpy.recarray.html#numpy.recarray ?
        self.data = np.zeros((2, 12))
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

        # calculate altitude
        alt = pvlib.atmosphere.pres2alt(float(pressure)*100)
        print("alt " + str(alt))
        new_row = np.append(new_row, alt)

        self.data = np.append(self.data, np.array([new_row]), axis=0)




    def get_data(self):
        return self.data

    def get_column(self, index: int = -1, name: str = ""):
        if index is not -1:
            if index in range(0, len(self.data) - 1):
                return self.data[:,index]
            else:
                return None
        elif name is not "":
            index = self.labels.index(str(name))
            if index in range(0, len(self.data) - 1):
                return self.data[:,self.labels.index(name)]
            else:
                return None
        else:
            return None












