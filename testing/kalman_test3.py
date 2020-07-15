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

data = np.array([process.get_column(index=0), process.get_column(index=11), process.get_column(name='accel_mag')])

data = data.T

print(data)

#print(process.get_column(index=0))

# todo use numpy
alt_list = []
vel_list = []

kf = kinematic_kf(dim=1, order=3, dt=.04)
transition_matrix = kf.F
print(kf.F)

# init altitude
kf.x[0] = data[0][1]
print('init', data[0][1])

kst = kinematic_state_transition(3, dt=.04)

kinematics = np.empty(np.append(0, kf.x).shape)
#kinematics.reshape(4, 1)
print(kinematics)

counter = 0
for time, alt, accel_mag in data:
    print(time, alt, accel_mag)
    if counter + 1 < data.shape[0]:
        delta_t = data[counter+1][0] - time

    kf.F = kinematic_state_transition(3, dt=delta_t)
    # adjust transition matrix
    grav = np.zeros_like(kf.F)

    grav[2][3] = -9.81 * delta_t
    # todo also add accel mag (negative accel mag useful approximation for vertical accel while going up)
    grav[2][3] += -accel_mag * delta_t

    print(grav, '\n', kf.F)
    kf.F = np.add(kf.F, grav)

    # update noise from timestep
    kf.Q = np.eye(kf.Q.shape[0]) * delta_t * 0.05
    kf.predict()
    kf.update(alt)
    #print(kinematics, np.append(time, kf.x))
    kinematics = np.vstack((kinematics, np.append(time, kf.x)))
    #print(kf.x)

    counter += 1

print(kinematics)

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


#v_data = v_data_euler
v_data = kinematics.T[2]

def ode(g, A, Cd, rho, m, v):
    return g - ((A * Cd * rho * (v ** 2) * 0.5) / m)


# possibly incorrect density estimate. wait, we can just use sense hat measured pressure lel
def density_estimate(rho0, altitude):
    #return rho0
    return rho0 * np.math.exp(-0.00012 * (altitude))


def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)

# Defining constants
A = 194.05E-4  #82.05E-4 # 82.05 cm^2 to m^2 (value from openrocket)
g = -9.81
Cd = 0.63
rho0 = 1.225    # kg/m^3
m = 23.511        # kg after burnout

STEP_SIZE = 0.01

apogee_estimate = np.ndarray.tolist(process.get_column(name="altitude")[0:burnout_index])

for test in range(burnout_index, len(process.get_data())):
    t = [process.get_column(name="time")[test]]
    h_pred = [h_data[test]]
    #print("aaaAAA")
    #print(h_pred)
    v_pred = [v_data[test]]

    for i in range(0, 10000):

        rho = density_estimate(rho0, h_pred[-1])
        #print(rho)
        # k1 calculation
        k1 = ode(g, A, Cd, rho, m, v_pred[-1])
        #print((k1 - g) * m)  # drag force
        # k2 calculation
        k2 = ode(g, A, Cd, rho, m, v_pred[-1] + k1 * 0.5)
        # k3 calculation
        k3 = ode(g, A, Cd, rho, m, v_pred[-1] + k2 * 0.5)
        # k4 calculation
        k4 = ode(g, A, Cd, rho, m, v_pred[-1] + k3)

        # saving v_n+1, h_n+1, t_n+1
        v_pred.append(v_pred[-1] + STEP_SIZE * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0)
        #print(v_pred[-1])
        #print(h_pred[-1] + STEP_SIZE * v_pred[-1])
        h_pred.append(h_pred[-1] + STEP_SIZE * v_pred[-1])
        t.append(t[-1] + STEP_SIZE)

        if h_pred[-1] < 0:
            apogee_estimate.append(0)
            break

        if v_pred[-1] < 0:
            print(str(i) + " done: " + str(h_pred[-1]) + " meters")
            apogee_estimate.append(h_pred[-1])
            break

print(apogee_estimate)

# moving average of results NOTE: we probably need to do some filtering because the moving averages have been integrated multiple times...
# the altitude has been integrated into velocity using 1st order Eulerian and velocity into altitude by Runge-Kutta

apogee_estimate_moving_avg = running_mean(apogee_estimate, 20)


# Plotting Altitude graph
plt.figure(1)
plt.title("Altitude")
h1, = plt.plot(process.get_column(name="time"), process.get_column(name="altitude"), color='g', label="Altimeter altitude")
h2, = plt.plot(kinematics.T[0], kinematics.T[1], color='r', label="Filtered Altitude")
h3, = plt.plot(process.get_column(name="time")[0:len(apogee_estimate)], apogee_estimate, color='b', label="Estimated apogee at point")
h4, = plt.plot(process.get_column(name="time")[0:len(apogee_estimate_moving_avg)], apogee_estimate_moving_avg, lw=4, color='purple', label="Estimated apogee at point with 20 moving avg")
h5, = plt.plot(process.get_column(name="time"), process.get_column(name="accel_z"), color='black', label="Accel z")
h6, = plt.plot(kinematics.T[0], kinematics.T[2], color='purple', label='vertical velocity')
h7, = plt.plot(kinematics.T[0], v_data_euler, color='brown', label='euler 1st order vertical velocity')
plt.legend(handles=[h1, h2, h3, h4, h5, h6, h7])
plt.show()
