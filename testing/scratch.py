import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise, kinematic_state_transition
import pvlib.atmosphere
import os

images_folder = os.path.join('images_tmp2')

IS_SUBSCALE = False
if IS_SUBSCALE:
    df = pd.read_csv("subscale_flight1.csv")

    # subscale, I think...
    # Defining constants
    A = 0.01005 # m^2 82.05e-4 #194.05E-4  #82.05E-4 # 82.05 cm^2 to m^2 (value from openrocket)
    g = -9.81
    Cd = 0.6635
    rho0 = 1.225    # kg/m^3
    m = 6.861        # kg after burnout
else:
    df = pd.read_csv('2020_3_7_11_10.csv', sep=',', index_col=False)

    # Defining constants
    A = 194.05E-4  #82.05E-4 # 82.05 cm^2 to m^2 (value from openrocket)
    g = -9.81
    Cd = 0.63
    rho0 = 1.225    # kg/m^3
    m = 23.511        # kg after burnout

STEP_SIZE = 0.01

def ode(g, A, Cd, rho, m, v):
    return g - ((A * Cd * rho * (v ** 2) * 0.5) / m)

# def density_estimate(pressure, temp):
#     rho = pressure * 100 / (287.05 * temp)
#     return rho

def density_estimate(rho0, altitude):
    #return rho0
    return rho0 * np.math.exp(-0.00012 * (altitude))

def drag_flaps_estimate(Cd, vel, flaps_extended):
    # values taken from a slide
    drag_increase_factor = 0
    if flaps_extended:
        drag_increase_factor = 0.0146 + 7.15E-05*vel + 1.21E-06*vel**2
    # print('drag_increase_factor', drag_increase_factor)
    return Cd * (1 + drag_increase_factor)

def calculate_apogee(time, alt, vel, pressure, temp, flaps_extended):
    t = [time]
    h_pred = [alt]
    v_pred = [vel]

    for i in range(10000):

        # print('start', t[-1], h_pred[-1], v_pred[-1])

        this_Cd = drag_flaps_estimate(Cd, v_pred[-1], flaps_extended)
        # print(Cd, this_Cd)

        rho = density_estimate(rho0, h_pred[-1])
        # print(rho)
        # k1 calculation
        k1 = ode(g, A, this_Cd, rho, m, v_pred[-1])
        #print((k1 - g) * m)  # drag force
        # k2 calculation
        k2 = ode(g, A, this_Cd, rho, m, v_pred[-1] + k1 * 0.5)
        # k3 calculation
        k3 = ode(g, A, this_Cd, rho, m, v_pred[-1] + k2 * 0.5)
        # k4 calculation
        k4 = ode(g, A, this_Cd, rho, m, v_pred[-1] + k3)

        # saving v_n+1, h_n+1, t_n+1
        v_pred.append(v_pred[-1] + STEP_SIZE * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0)
        #print(v_pred[-1])
        #print(h_pred[-1] + STEP_SIZE * v_pred[-1])
        h_pred.append(h_pred[-1] + STEP_SIZE * v_pred[-1])
        t.append(t[-1] + STEP_SIZE)

        # print('next ', t[-1], h_pred[-1], v_pred[-1])

        if h_pred[-1] < 0:
            return h_pred[-1]

        if v_pred[-1] < 0:
            return h_pred[-1]


def my_pres2alt(pressure: float):
    return pvlib.atmosphere.pres2alt(pressure*100)

pres2alt_vectorized = np.vectorize(my_pres2alt)



print(df)
df['pressure'] = pd.to_numeric(df['pressure'])
print(df)
df['alt'] = my_pres2alt(df['pressure'])
print(df)

df['alt'] = df['alt'] - df.loc[0, 'alt']

f = KalmanFilter(dim_x=3, dim_z=2)

f.x = np.array([0, 0, 0])

f.F = kinematic_state_transition(2, 0.04)
print(f.F)

f.H = np.array([[1, 0, 0], [0, 0, 1]])

f.P *= 1000
f.R *= 5

print(f.P)
print(f.R)

# f.Q = Q_discrete_white_noise(dim=2, dt=0.1, var=0.13)

df['vel_euler'] = 0

df['pred_alt'] = 0
df['pred_vel'] = 0
df['pred_acc'] = 0
df['pred_apogee'] = 0
df['pred_apogee_flaps'] = 0

# full-scale vs sub-scale data format
takeoff_idx = df.index[(df['event'] == 'Event.TAKE_OFF') | (df['event'] == 'launch')]
burnout_idx = df.index[(df['event'] == 'Event.MOTOR_BURNOUT') | (df['event'] == 'burnout')]
apogee_idx = df.index[(df['event'] == 'Event.APOGEE') | (df['event'] == 'apogee')]

print(takeoff_idx, burnout_idx)

df['kalman_y-alt'] = 0
df['kalman_y-acc'] = 0

delta_t = 0.04
calculated_vel = 0
for idx, row in df.iterrows():
    if idx > 0:
        delta_t = row['time'] - df.loc[idx - 1, 'time']
        calculated_vel = (row['alt'] - df.loc[idx - 1, 'alt']) / delta_t
        df.loc[idx, 'vel_euler'] = calculated_vel

    # if idx < burnout_idx:
    #     f.x = np.array([row['alt'], calculated_vel, 0])
    #     continue
    f.F = kinematic_state_transition(2, delta_t)
    z = (row['alt'], 9.81 * (-1 + row['az']))
    f.predict()
    df.loc[idx,'pred_alt'] = f.x[0]
    df.loc[idx,'pred_vel'] = f.x[1]
    df.loc[idx,'pred_acc'] = f.x[2]
    # print(f.x[0], row['alt'])
    f.update(z)

    # print(f.y)

    df.loc[idx, 'kalman_y-alt'] = f.y[0]
    df.loc[idx, 'kalman_y-acc'] = f.y[1]

    pred_apogee = calculate_apogee(row['time'], df.loc[idx, 'pred_alt'], df.loc[idx, 'pred_vel'], row['pressure'], row['temperature'], flaps_extended=False)
    pred_apogee_flaps = calculate_apogee(row['time'], df.loc[idx, 'pred_alt'], df.loc[idx, 'pred_vel'], row['pressure'], row['temperature'], flaps_extended=True)

    # print(pred_apogee, pred_apogee_flaps)

    df.loc[idx, 'pred_apogee'] = pred_apogee
    df.loc[idx, 'pred_apogee_flaps'] = pred_apogee_flaps



    # if row['time'] > 10:
    #     exit(0)

plt.rcParams['figure.figsize'] = [8.0, 6.0]
plt.rcParams['figure.dpi'] = 300

df = df[min(takeoff_idx):min(apogee_idx)]

popup_windows = False

plt.figure(6)
plt.plot(df['time'], df['alt'], label='altitude (barometer)')

plt.plot(df['time'], df['pred_alt'], label='altitude (Kalman)', linestyle='dashed')
plt.plot(df['time'], df['pred_vel'], label='velocity (Kalman)')
plt.plot(df['time'], df['pred_acc'], label='acceleration (Kalman)')
plt.plot(df['time'], df['az']*9.81 - 9.81, label='acceleration')
plt.plot(df['time'], df['pred_apogee'], label='apogee (predicted)')
plt.plot(df['time'], df['pred_apogee_flaps'], label='apogee (predicted w/ flaps)', linestyle='dashed')

plt.xlabel("time (s)")
plt.ylabel("meters")
plt.legend()
plt.savefig(os.path.join(images_folder, 'multiplot.png'), bbox_inches='tight')
if popup_windows:
    plt.show()
else:
    plt.clf()

plt.figure(6)
# plt.plot(df['time'], df['alt'], label='alt')
# plt.plot(df['time'], df['pred_alt'], label='alt_kalman')
plt.scatter(df['time'], df['vel_euler'], label='velocity (Euler 1st-order approx)', s=2, c='r')
plt.plot(df['time'], df['pred_vel'], label='velocity (Kalman)')
plt.plot(df['time'], df['az']*9.81 - 9.81, label='acceleration')
plt.plot(df['time'], df['pred_acc'], label='acceleration (Kalman)')
# plt.plot(df['time'], df['pred_apogee'], label='apogee_pred')
# plt.plot(df['time'], df['pred_apogee_flaps'], label='apogee_pred_flaps')

plt.xlabel("time (s)")
plt.ylabel("m/s")
plt.legend()
plt.savefig(os.path.join(images_folder, 'velocity_plot.png'), bbox_inches='tight')
if popup_windows:
    plt.show()
else:
    plt.clf()

fig = plt.figure(6)
plt.plot(df['time'], df['kalman_y-alt'], label='Altitude Residual')
plt.plot(df['time'], df['kalman_y-acc'], label='Acceleration Residual')
# plt.plot(df['time'], df['pred_alt'], label='alt_kalman')
# plt.plot(df['time'], df['pred_vel'], label='vel_kalman')
# plt.plot(df['time'], df['pred_acc'], label='accel_z_kalman')
# plt.plot(df['time'], df['pred_apogee'], label='apogee_pred')
# plt.plot(df['time'], df['pred_apogee_flaps'], label='apogee_pred_flaps')
# plt.plot(df['time'], df['az']*9.81 - 9.81, label='accel_z')
plt.xlabel("time (s)")
plt.legend()
plt.savefig(os.path.join(images_folder, 'residuals.png'), bbox_inches='tight')
if popup_windows:
    plt.show()
else:
    plt.clf()

plt.figure(6)
plt.plot(df['time'], df['roll'], label='roll')
plt.plot(df['time'], df['pitch'], label='pitch')
plt.plot(df['time'], df['yaw'], label='yaw')
plt.legend()
plt.savefig(os.path.join(images_folder, 'gyro.png'), bbox_inches='tight')
if popup_windows:
    plt.show()
else:
    plt.clf()