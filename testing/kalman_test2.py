import csv

from filterpy.kalman import KalmanFilter
from filterpy.common import kinematic_kf, kinematic_state_transition
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

alt_readings = np.ndarray.tolist((process.get_column(index=11)))
accel_magnitudes = np.ndarray.tolist((process.get_column(name='accel_mag')))
timesteps = np.ndarray.tolist((process.get_column(index=0)))

data = np.array([process.get_column(index=0), process.get_column(index=11), process.get_column(name='accel_z')])

data = data.T

print(data)

#print(process.get_column(index=0))

# todo use numpy
alt_list = []
vel_list = []

kf = kinematic_kf(dim=1, order=3, dt=1.)
transition_matrix = kf.F
print(kf.F)
kf.Q *= 0.01
print('noise', kf.Q)

# init altitude
kf.x[0] = data[0][1]
print('init', data[0][1])

kst = kinematic_state_transition(3, dt=.04)

kinematics = np.empty(np.append(0, kf.x).shape)
#print(kinematics)

counter = 0
for time, alt, accel_z in data:
    #print(time, alt, accel_mag)
    if counter + 1 < data.shape[0]:
        delta_t = data[counter+1][0] - time

    kf.F = kinematic_state_transition(3, dt=delta_t)
    # adjust transition matrix
    grav = np.zeros_like(kf.F)

    grav[2][3] = -9.81 * delta_t
    #todo also add accel_z
    grav[2][3] += accel_z * delta_t

    #print(grav, '\n', kf.F)
    kf.F = np.add(kf.F, grav)

    # update noise from timestep
    kf.Q = np.eye(kf.Q.shape[0]) * delta_t

    kf.predict()
    kf.update(alt)
    #print(kinematics, np.append(time, kf.x))
    kinematics = np.vstack((kinematics, np.append(time, kf.x)))
    #print(kf.x)

    counter += 1

#print(kinematics)

alt_list = kinematics.T[1]
#print(kinematics.T[1])
vel_list = kinematics.T[2]

h_data = alt_list
v_data_euler = [0.]

#TODO move velocity calculation to processor
for i in range(1, len(kinematics.T[0])):
    vel = (h_data[i] - h_data[i-1]) / (kinematics[i][0] - kinematics[i-1][0])
    if vel > -100 and vel < 300:
        v_data_euler.append(vel)
    else:
        v_data_euler.append(0)


v_data = v_data_euler



plt.figure(1)
plt.title("Altitude")
h1, = plt.plot(process.get_column(name="time"), process.get_column(name="altitude"), color='g', label="Altimeter altitude")
h2, = plt.plot(kinematics.T[0], alt_list, color='r', label="Kalman filter altitude")
h3, = plt.plot(kinematics.T[0], vel_list, color='b', label="Kalman filter velocity")
h4, = plt.plot(kinematics.T[0], v_data_euler, color='r', label="Kalman filter euler velocity")
plt.legend(handles=[h1, h2, h3, h4])
plt.show()

plt.figure(2)
plt.title("Velocity")
h3, = plt.plot(kinematics.T[0], vel_list, color='b', label="Kalman filter velocity")
h4, = plt.plot(kinematics.T[0], v_data_euler, color='r', label="Kalman filter euler velocity")
plt.legend(handles=[h3, h4])
plt.show()
