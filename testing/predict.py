import scipy.interpolate as interpolate
import matplotlib.pyplot as plt
import csv
import math
from datetime import datetime

# Equation representing the acceleration of motor after motor burn out
def ode(g, A, Cd, rho, m, v):
    return g - ((A * Cd * rho *(v ** 2) * 0.5) / m)

# Stratologger Data
t_alt = []
h_alt = []
v_alt = []
with open("SOD02.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    head = True
    for row in csv_reader:
        if head:
            head = False
        else:
            t_alt.append(float(row[0]))
            h_alt.append(float(row[1]))
            v_alt.append(float(row[2]))

# SenseHAT data
t_sense = []
h_sense = []
v_sense = []
with open("subscale_data_cleaned1.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    head = True
    for row in csv_reader:
        if head:
            head = False
        else:
            t_sense.append(float(row[0]))
            h_sense.append(float(row[8]))
            v_sense.append(float(row[10]))

# Defining constants
A = (4.33*0.165*4+(2.012 ** 2)*math.pi)/144.00 # projected area of the rocket (ft^2)
g = -32.17405 # standard gravity (ft/s^2)
Cd = 0.665 # drag coefficient
rho = 0.0023769 # air density (slug/ft^3) --> assumed constant but will try variable density
m = 0.470099 # mass of rocket after motor burnout (slug)


# Looking at the graph, I selected the altitude and velocity at motor burnout obtained from SenseHAT
h_burnout = h_sense[28]
v_burnout = v_sense[28]
t_burnout = t_sense[28]

v_pred = [v_burnout] # keeps track of predicted velocity by Runge-Kutta, initial velocity is the velocity at motor burnout
h_pred = [h_burnout] # keeps track of predicted altitude by Runge-Kutta, initial altitude is the altitude at motor burnout
t = [t_burnout]

# Defining constants specific to Runge-Kutta
STEP_SIZE = 0.01
RANGE = 2000

start = datetime.now() # variable to measure computation time

# NOTE: I used a fixed number of iteration --> this could be shortened by stopping when velocity becomes negative
for i in range(RANGE):
    # k1 calculation
    k1 = ode(g, A, Cd, rho, m, v_pred[-1])
    # k2 calculation
    k2 = ode(g, A, Cd, rho, m, v_pred[-1] + k1 * 0.5)
    # k3 calculation
    k3 = ode(g, A, Cd, rho, m, v_pred[-1] + k2 * 0.5)
    # k4 calculation
    k4 = ode(g, A, Cd, rho, m, v_pred[-1] + k3)

    # saving v_n+1, h_n+1, t_n+1
    v_pred.append(v_pred[-1] + STEP_SIZE * (k1 + 2.0 * k2 + 2.0 * k3 + k4)/6.0)
    h_pred.append(h_pred[-1] + STEP_SIZE * v_pred[-1])
    t.append(t[-1] + STEP_SIZE)

print(datetime.now() - start) # time for computation time

# Plotting Velocity graph
plt.figure(1)
plt.title("Velocity")
v1, = plt.plot(t_sense[25:], v_sense[25:], color='r', label="SenseHAT velocity")
v2, = plt.plot(t_alt, v_alt, color='b', label="Altimeter velocity")
v3, = plt.plot(t, v_pred, color='g', label="Predicted velocity")
plt.legend(handles=[v1, v2, v3])

# Plotting Altitude graph
plt.figure(2)
plt.title("Altitude")
h1, = plt.plot(t_sense, h_sense, color='r', label="Actual altitude")
h2, = plt.plot(t_alt, h_alt, color='b', label="Altimeter altitude")
h3, = plt.plot(t, h_pred, color='g', label="Predicted altitude")
plt.legend(handles=[h1, h2, h3])
plt.show()