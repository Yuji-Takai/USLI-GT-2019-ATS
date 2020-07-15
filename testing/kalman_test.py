import csv

from filterpy.kalman import KalmanFilter
# see https://filterpy.readthedocs.io/en/latest/kalman/KalmanFilter.html
import numpy as np
import matplotlib.pyplot as plt

from processor import Processor

burnout_index = 0
counter = 0

process = Processor()

with open("2020_3_7_11_10.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    head = True
    for row in csv_reader:
        if head:
            head = False
        else:
            print(*row)
            process.append_data(*row)
            if len(row[-1]) > 0:
                print(row[-1])

            if row[-1] == 'burnout':
                burnout_index = counter

            counter += 1

            if row[-1] == 'apogee':
                break

sensor_readings = np.ndarray.tolist((process.get_column(index=11)))
timesteps = np.ndarray.tolist((process.get_column(index=0)))

#print(process.get_column(index=0))

# todo use numpy
alt_list = []
vel_list = []

f = KalmanFilter(dim_x=2, dim_z=1)

f.x = np.array([2., 0.])

transition_matrix = np.array([[1., 1.], [0., 1.]])

f.F = transition_matrix

f.H = np.array([[1., 0.]])

f.P = np.array([[1000., 0.], [0., 1000.]])

f.R = np.array([[5.]])

from filterpy.common import Q_discrete_white_noise

f.Q = Q_discrete_white_noise(dim=2, dt=2., var=0.13)


for i in range(0, len(sensor_readings)):
    sensor_reading = sensor_readings[i]
    if i + 1 < len(sensor_readings):
        delta_t = timesteps[i+1] - timesteps[i]

    #print(delta_t)
    f.F = np.array([[1., delta_t], [0., 1.]])
    print(f.F)
    #print(sensor_reading)
    z = sensor_reading
    f.predict()
    f.update(z)
    alt_list.append(f.x[0])
    vel_list.append(f.x[1])

#print(alt_list)


plt.figure(1)
plt.title("Altitude")
h1, = plt.plot(process.get_column(name="time"), process.get_column(name="altitude"), color='g', label="Altimeter altitude")
h2, = plt.plot(process.get_column(name="time"), alt_list, color='r', label="Kalman filter altitude")
h3, = plt.plot(process.get_column(name="time"), vel_list, color='b', label="Kalman filter velocity")
plt.legend(handles=[h1, h2, h3])
plt.show()

plt.figure(2)
plt.title("Velocity")
h3, = plt.plot(process.get_column(name="time"), vel_list, color='b', label="Kalman filter velocity")
plt.legend(handles=[h3])
plt.show()
