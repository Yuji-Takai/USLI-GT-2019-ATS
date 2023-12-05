import csv

from filterpy.kalman import KalmanFilter
from filterpy.common import kinematic_kf, kinematic_state_transition
# see https://filterpy.readthedocs.io/en/latest/kalman/KalmanFilter.html
import numpy as np
import matplotlib.pyplot as plt
from filterpy.common import Q_discrete_white_noise

from processor import Processor

burnout_index = 0
counter = 0

process = Processor()

with open("subscale_flight1.csv", "r") as csv_file:
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

kf = kinematic_kf(dim=1, order=2, dt=.04)
transition_matrix = kf.F
print(kf.F)

# kf.Q = Q_discrete_white_noise(dim=1, dt=0.1, var=0.13)
# kf.R = Q_discrete_white_noise(dim=1, dt=0.1, var=0.13)

# init altitude
kf.x[0] = data[0][1]
print('init', data[0][1])

kst = kinematic_state_transition(2, dt=.04)

kinematics = np.empty(np.append(0, kf.x).shape)
kinematics_Q = np.empty(np.append(0, kf.Q).shape)
kinematics_P = np.empty(np.append(0, kf.P).shape)
kinematics_R = np.empty(np.append(0, kf.R).shape)
kinematics_K = np.empty(np.append(0, kf.K).shape)
kinematics_y = np.empty(np.append(0, kf.y).shape)
#kinematics.reshape(4, 1)
print(kinematics)

v_data_euler = [0., 0]

#TODO move velocity calculation to processor
for i in range(1, len(data)):
    time, alt, accel_mag = data[i]
    last_time, last_alt, last_accel_mag = data[i-1]
    vel = (alt - last_alt) / (time - last_time)
    print('vel', vel)
    if vel > -100 and vel < 300:
        v_data_euler.append(vel)
    else:
        v_data_euler.append(0)

counter = 0
delta_t = 0.04
for time, alt, accel_mag in data:
    
    if counter - 1 >= 0:
        delta_t = time - data[counter-1][0]


    
    print(time, delta_t, alt, accel_mag)

    

    kf.F = kinematic_state_transition(2, dt=delta_t)
    # print('kf.F', kf.F)
    # adjust transition matrix
    grav = np.zeros_like(kf.F)

    # grav[2][3] = -9.81 - accel_mag

    # grav[2][3] = -9.81 * delta_t
    # # todo also add accel mag (negative accel mag useful approximation for vertical accel while going up)
    # grav[2][3] += -accel_mag * delta_t

    grav[2][2] = (-9.81 + accel_mag*9.81)

    print(grav, '\n', kf.F, '\n', np.add(kf.F, grav))
    # kf.F = np.add(kf.F, grav)

    # update noise from timestep

    print('before kf.Q', '\n', kf.Q)
    # kf.Q = np.eye(kf.Q.shape[0]) * delta_t * 0.05 #* 0.05
    kf.predict()

    kf.update(alt)

    #print(kinematics, np.append(time, kf.x))
    kinematics = np.vstack((kinematics, np.append(time, kf.x)))
    kinematics_Q = np.vstack((kinematics_Q, np.append(time, kf.Q)))
    kinematics_P = np.vstack((kinematics_P, np.append(time, kf.P)))
    kinematics_R = np.vstack((kinematics_R, np.append(time, kf.R)))
    kinematics_K = np.vstack((kinematics_K, np.append(time, kf.K)))
    kinematics_y = np.vstack((kinematics_y, np.append(time, kf.y)))
    #print(kf.x)

    counter += 1

print(kinematics)

alt_list = kinematics.T[1]
#print(kinematics.T[1])
vel_list = kinematics.T[2]

h_data = alt_list
# v_data_euler = [0.]

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
# A = (4.33*0.165*4+(2.012 ** 2)*math.pi)/144.00 # projected area of the rocket (ft^2)
# g = -32.17405 # standard gravity (ft/s^2)
# Cd = 0.6635 #0.665 # drag coefficient
# rho0 = 0.0023769 # air density (slug/ft^3) --> assumed constant but will try variable density
# m = 0.470099 # mass of rocket after motor burnout (slug)

# Defining constants
A = 0.01005 # m^2 82.05e-4 #194.05E-4  #82.05E-4 # 82.05 cm^2 to m^2 (value from openrocket)
g = -9.81
Cd = 0.6635
rho0 = 1.225    # kg/m^3
m = 6.861        # kg after burnout

STEP_SIZE = 0.01

burnout_index = 1

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
            # print(str(i) + " done: " + str(h_pred[-1]) + " meters")
            apogee_estimate.append(h_pred[-1])
            break

print(apogee_estimate)

# moving average of results NOTE: we probably need to do some filtering because the moving averages have been integrated multiple times...
# the altitude has been integrated into velocity using 1st order Eulerian and velocity into altitude by Runge-Kutta

# apogee_estimate_moving_avg = running_mean(apogee_estimate, 20)

# Plotting Altitude graph
plt.figure(0)
plt.title("Altitude")
h1, = plt.plot(process.get_column(name="time"), process.get_column(name="altitude"), color='g', label="Altimeter altitude")
# h2, = plt.plot(kinematics.T[0], kinematics.T[1], color='r', label="Filtered Altitude")
# h3, = plt.plot(process.get_column(name="time")[0:len(apogee_estimate)], apogee_estimate, color='b', label="Estimated apogee at point")
# h4, = plt.plot(process.get_column(name="time")[0:len(apogee_estimate_moving_avg)], apogee_estimate_moving_avg, lw=4, color='purple', label="Estimated apogee at point with 20 moving avg")
# h5, = plt.plot(process.get_column(name="time"), process.get_column(name="accel_z"), color='black', label="Accel z")
# h6, = plt.plot(kinematics.T[0], kinematics.T[2], color='purple', label='vertical velocity')
# h7, = plt.plot(kinematics.T[0], v_data_euler, color='brown', label='euler 1st order vertical velocity')
# plt.legend(handles=[h1, h2, h3, h4, h5, h6, h7])
plt.show()

# Plotting Altitude graph
plt.figure(1)
plt.title("Altitude")
h1, = plt.plot(process.get_column(name="time"), process.get_column(name="altitude"), color='g', label="Altimeter altitude")
h2, = plt.plot(kinematics.T[0], kinematics.T[1], color='r', label="Filtered Altitude")
h3, = plt.plot(process.get_column(name="time")[0:len(apogee_estimate)], apogee_estimate, color='b', label="Estimated apogee at point")
# h4, = plt.plot(process.get_column(name="time")[0:len(apogee_estimate_moving_avg)], apogee_estimate_moving_avg, lw=4, color='purple', label="Estimated apogee at point with 20 moving avg")
h5, = plt.plot(process.get_column(name="time"), process.get_column(name="accel_z"), color='black', label="Accel z")
h6, = plt.plot(kinematics.T[0], kinematics.T[2], color='purple', label='vertical velocity')
h7, = plt.plot(kinematics.T[0], v_data_euler, color='brown', label='euler 1st order vertical velocity')
plt.legend(handles=[h1, h2, h3, h5, h6, h7])
plt.show()

print(np.array(v_data_euler))
print(kinematics.T[0])

# Plotting Altitude graph
plt.figure(2)
plt.title("Altitude")
# h1, = plt.plot(process.get_column(name="time"), process.get_column(name="altitude"), color='g', label="Altimeter altitude")
# h2, = plt.plot(kinematics.T[0], kinematics.T[1], color='r', label="Filtered Altitude")
# h3, = plt.plot(process.get_column(name="time")[0:len(apogee_estimate)], apogee_estimate, color='b', label="Estimated apogee at point")
# h4, = plt.plot(process.get_column(name="time")[0:len(apogee_estimate_moving_avg)], apogee_estimate_moving_avg, lw=4, color='purple', label="Estimated apogee at point with 20 moving avg")
h5, = plt.plot(process.get_column(name="time"), process.get_column(name="accel_z"), color='black', label="Accel z")
h6, = plt.plot(kinematics.T[0], kinematics.T[2], color='purple', label='vertical velocity')
h7 = plt.scatter(x=kinematics.T[0], y=np.array(v_data_euler), color='brown', label='euler 1st order vertical velocity')
# plt.legend(handles=[h1, h2, h3, h4, h5, h6, h7])
plt.show()

plt.figure(4)
plt.title("bbb")
print('k_Q', kinematics_Q.T)
print('k_P size', kinematics_P.T.shape)
print('k_P', kinematics_P.T)
print('k_R', kinematics_R.T)
print('k_K', kinematics_K.T)
print('k_y', kinematics_y.T)
h1 = plt.scatter(kinematics_Q.T[0], kinematics_Q.T[1], color='g', label="kinematics_Q")
# h2, = plt.plot(kinematics_P.T[0], kinematics_P.T[1], color='r', label="kinematics_P[1]")
# h21, = plt.plot(kinematics_P.T[0], kinematics_P.T[2], color='r', label="kinematics_P[2]")
# h22, = plt.plot(kinematics_P.T[0], kinematics_P.T[3], color='r', label="kinematics_P[3]")
h3, = plt.plot(kinematics_R.T[0], kinematics_R.T[1], color='b', label="kinematics_R")
h4, = plt.plot(kinematics_K.T[0], kinematics_K.T[1], color='brown', label="kinematics_K")
h5 = plt.scatter(kinematics_y.T[0], kinematics_y.T[1], color='purple', label="kinematics_y (Kalman Residual)")
# h1, = plt.plot(process.get_column(name="time"), process.get_column(name="altitude"), color='g', label="Altimeter altitude")
# h2, = plt.plot(kinematics.T[0], kinematics.T[1], color='r', label="Filtered Altitude")
# h3, = plt.plot(process.get_column(name="time")[0:len(apogee_estimate)], apogee_estimate, color='b', label="Estimated apogee at point")
# h4, = plt.plot(process.get_column(name="time")[0:len(apogee_estimate_moving_avg)], apogee_estimate_moving_avg, lw=4, color='purple', label="Estimated apogee at point with 20 moving avg")
# h5, = plt.plot(process.get_column(name="time"), process.get_column(name="accel_z"), color='black', label="Accel z")
# h6, = plt.plot(kinematics.T[0], kinematics.T[2], color='purple', label='vertical velocity')
# h7, = plt.plot(kinematics.T[0], v_data_euler, color='brown', label='euler 1st order vertical velocity')
plt.legend(handles=[h1, h3, h4, h5])
plt.show()

plt.figure(5)

for i in range(1, kinematics_P.T.shape[0]):
    plt.plot(kinematics_P.T[0], kinematics_P.T[i], label="kinematics_P[{}]".format(i))
plt.legend()
plt.show()

plt.figure(6)

h5, = plt.plot(process.get_column(name="time"), process.get_column(name="accel_z"), color='black', label="Accel z")

for i in range(1, kinematics.T.shape[0]):
    plt.plot(kinematics.T[0], kinematics.T[i], label="kinematics_T[{}]".format(i))
plt.legend()
plt.show()
