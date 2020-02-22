from processor import Processor
import csv
import numpy as np
import math as math

import matplotlib.pyplot as plt

process = Processor()

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
                pass
            if row[-1] == 'apogee':
                break


#print(process.get_column(0))
#print(process.get_data()[:,8])

#print(len(process.get_data()[:,8]))

time_data = np.ndarray.tolist(process.get_column(name="time"))

barometer_data = np.ndarray.tolist(process.get_column(name="pressure"))

accel_mag_data = process.get_column(name="accel_mag")


# # Plotting Velocity graph
# plt.figure(1)
# plt.title("Accel magnitude")
# a1, = plt.scatter(*process.get_data()[:,0], *process.get_data()[:,1], color='red')
# #a1, = plt.plot(t_sense[25:], accel_derived[25:], color='purple', label="derived acceleration")
# plt.show()

# xyz = np.random.random((1223, 2))
#
# print(xyz[:,0])
# print(len(xyz[:,0]))
#
# # Plotting Altitude graph
# plt.figure(2)
# plt.title("Altitude")
# f1, = plt.plot(xyz[:,0], xyz[:,1], color='r', label="Actual altitude")
# plt.legend(handles=[f1])
# plt.show()

plt.figure(1)
plt.title("aaa")
h1, = plt.plot(time_data, accel_mag_data, label='accel magnitude')

plt.legend(handles=[h1])
plt.show()

plt.figure(1)
plt.title("bbb")
p1, = plt.plot(time_data, process.get_data()[:,4], color='r', label='pitch')
p2, = plt.plot(time_data, process.get_data()[:,5], color='b', label='roll')
p3, = plt.plot(time_data, process.get_data()[:,6], color='g', label='yaw')
plt.legend(handles=[p1, p2, p3])
plt.show()


# https://stackoverflow.com/questions/55169099/animating-a-3d-vector-with-matplotlib
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))

# TODO fix visualization so it displays pitch roll and yaw correctly
# see https://math.stackexchange.com/questions/2618527/converting-from-yaw-pitch-roll-to-vector

def get_arrow(iter):
    theta = process.get_data()[:, 4][iter]*(math.pi/180)
    phi = process.get_data()[:, 6][iter]*(math.pi/180)
    x = 0
    y = 0
    z = 0
    u = math.cos(phi) * math.cos(theta)
    v = math.sin(phi) * math.cos(theta)
    w = math.sin(theta)
    return x,y,z,u,v,w

quiver = ax.quiver(*get_arrow(0))

ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_zlim(-2, 2)

def update(theta):
    global quiver
    quiver.remove()
    quiver = ax.quiver(*get_arrow(theta))

ani = FuncAnimation(fig, update, frames=np.arange(2, len(process.get_data())), interval=1)
plt.show()




