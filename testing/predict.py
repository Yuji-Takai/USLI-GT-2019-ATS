import scipy.interpolate as interpolate
import matplotlib.pyplot as plt
import csv
import math
from datetime import datetime

# what is a slug and why is air measured in slugs/ft^3 - Alex

# Equation representing the acceleration of motor after motor burn out
def ode(g, A, Cd, rho, m, v):
    return g - ((A * Cd * rho *(v ** 2) * 0.5) / m)

# wip, do not use
def derive_Cd(g, A, rho, m, v, accel):
    return (m * (g - accel)) / (A * rho * (v ** 2) * 0.5)

# possibly incorrect density estimate. wait, we can just use sense hat measured pressure lel
def density_estimate(rho0, altitude):
    #return rho0
    return rho0*math.exp(-0.00012*(altitude*0.3048))

# start index (28 = burnout, about 10 steps per second)
start_index = 28


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
accel_derived = []
accel_derived.append(0)
cd_derived = []
cd_derived.append(0)

# Defining constants
A = (4.33*0.165*4+(2.012 ** 2)*math.pi)/144.00 # projected area of the rocket (ft^2)
g = -32.17405 # standard gravity (ft/s^2)
Cd = 0.6635 #0.665 # drag coefficient
rho0 = 0.0023769 # air density (slug/ft^3) --> assumed constant but will try variable density
m = 0.470099 # mass of rocket after motor burnout (slug)

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

            #first order vertical acceleration approximation, there is probably a better way to do this
            #maybe use kalman filter?
            if (len(t_sense) > 1):
                accel = (v_sense[-1] - v_sense[-2]) / (t_sense[-1] - t_sense[-2])
                if (accel < -1000):
                    accel = 0
                #print(accel)
                accel_derived.append(accel)

                cd = derive_Cd(g, A, rho0, m, v_sense[-1], accel_derived[-1])
                if cd < -2:
                    #print(cd)
                    cd = 0

                cd_derived.append(cd)




# Looking at the graph, I selected the altitude and velocity at motor burnout obtained from SenseHAT
h_burnout = h_sense[start_index]
v_burnout = v_sense[start_index]
t_burnout = t_sense[start_index]

v_pred = [v_burnout] # keeps track of predicted velocity by Runge-Kutta, initial velocity is the velocity at motor burnout
h_pred = [h_burnout] # keeps track of predicted altitude by Runge-Kutta, initial altitude is the altitude at motor burnout

cd_measured = []

t = [t_burnout]

# Defining constants specific to Runge-Kutta
STEP_SIZE = 0.01
RANGE = 2000

start = datetime.now() # variable to measure computation time

# NOTE: I used a fixed number of iteration --> this could be shortened by stopping when velocity becomes negative
while (v_pred[-1] > 0):
    rho = density_estimate(rho0, h_pred[-1])
    #print(rho)
    # k1 calculation
    k1 = ode(g, A, Cd, rho, m, v_pred[-1])
    print((k1-g)*m) #drag force
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

    if v_pred[-1] < 0:
        print("done")
        break

print(datetime.now() - start) # time for computation time

print(h_pred[-1])

# Plotting Velocity graph
plt.figure(1)
plt.title("Velocity")
v1, = plt.plot(t_sense[25:], v_sense[25:], color='r', label="SenseHAT velocity")
v2, = plt.plot(t_alt, v_alt, color='b', label="Altimeter velocity")
v3, = plt.plot(t, v_pred, color='g', label="Predicted velocity")
#a1, = plt.plot(t_sense[25:], accel_derived[25:], color='purple', label="derived acceleration")
plt.legend(handles=[v1, v2, v3])

# Plotting Altitude graph
plt.figure(2)
plt.title("Altitude")
h1, = plt.plot(t_sense, h_sense, color='r', label="Actual altitude")
h2, = plt.plot(t_alt, h_alt, color='b', label="Altimeter altitude")
h3, = plt.plot(t, h_pred, color='g', label="Predicted altitude")
plt.axhline(y=2500, color="y", linestyle="-")
plt.legend(handles=[h1, h2, h3])
plt.show()

