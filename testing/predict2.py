import csv
import math

from processor import Processor
import csv
import numpy as np
import math as math

import matplotlib.pyplot as plt

process = Processor()

burnout_index = 0

counter = 0

with open("flight1.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    head = True
    for row in csv_reader:
        if head:
            head = False
        else:
            #print(*row)
            process.append_data(*row)
            if len(row[-1]) > 0:
                print(row[-1])

            if row[-1] == 'burnout':
                burnout_index = counter

            counter += 1

            if row[-1] == 'apogee':
                break


def ode(g, A, Cd, rho, m, v):
    return g - ((A * Cd * rho * (v ** 2) * 0.5) / m)

# possibly incorrect density estimate. wait, we can just use sense hat measured pressure lel
def density_estimate(rho0, altitude):
    #return rho0
    return rho0*math.exp(-0.00012*(altitude*0.3048))

# Defining constants
A = 82.05E-4 # 82.05 cm^2 to m^2 (value from openrocket)
g = -9.81
Cd = 0.665
rho0 = 1.225    # kg/m^3
m = 5.11        # kg after burnout

STEP_SIZE = 0.01

apogee_estimate = np.ndarray.tolist(process.get_column(name="altitude")[0:burnout_index])

h_data = np.ndarray.tolist(process.get_column(index=11))

v_data = [0]

#TODO move velocity calculation to processor
for i in range(1, len(h_data)):
    v_data.append((h_data[i] - h_data[i-1]) / (process.get_column(name="time")[i] - process.get_column(name="time")[i-1]))

print(burnout_index)
#print(v_data)


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

        if v_pred[-1] < 0:
            print(str(i) + " done: " + str(h_pred[-1]) + " meters")
            apogee_estimate.append(h_pred[-1])
            break

print(apogee_estimate)

# moving average of results NOTE: we probably need to do some filtering because the moving averages have been integrated multiple times...
# the altitude has been integrated into velocity using 1st order Eulerian and velocity into altitude by Runge-Kutta

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)

apogee_estimate_moving_avg = running_mean(apogee_estimate, 10)


# Plotting Altitude graph
plt.figure(1)
plt.title("Altitude")
h1, = plt.plot(process.get_column(name="time"), process.get_column(name="altitude"), color='r', label="Altimeter altitude")
h2, = plt.plot(process.get_column(name="time")[0:len(apogee_estimate)], apogee_estimate, color='b', label="Estimated apogee at point")
h3, = plt.plot(process.get_column(name="time")[0:len(apogee_estimate_moving_avg)], apogee_estimate_moving_avg, lw=4, color='purple', label="Estimated apogee at point with 10 moving avg")
plt.legend(handles=[h1, h2, h3])
plt.show()
