import matplotlib.pyplot as plt
import csv
from sensor_data import SensorData
from event import Event
from ats_math import pressure2alt, feet2meter, inch2meter, oz2kg, alt2rho
import math
from constants import STANDARD_GRAVITY, STEP_SIZE

def ode(g, A, Cd, rho, m, v):
    '''
    returns the acceleration of the launch vehicle during the coast state
    the launch vehicle's equation of motion is simplified to be only the sum of weight and drag
    '''
    return -g - ((A * Cd * rho *(v ** 2) * 0.5) / m)

sense_hat_data, pitch, roll, yaw = [], [], [], []
events = {}
with open("2020_3_7_11_10.csv", 'rU') as f:
    reader = csv.reader(f, delimiter=",")
    head = True
    try:
        for row in reader:
            if head:
                head = False
            else:
                sense_hat_data.append(SensorData(time=float(row[0]), 
                    ax=float(row[1]), ay=float(row[2]), az=float(row[3]), 
                    pitch=float(row[4]), roll=float(row[5]), yaw=float(row[6]), 
                    temp=float(row[7]), pressure=float(row[8])))
                if row[9] == "Event.TAKE_OFF":
                    sense_hat_data[-1].event = Event.TAKE_OFF
                    events["Take off"] = sense_hat_data[-1].time
                elif row[9] == "Event.MOTOR_BURNOUT":
                    sense_hat_data[-1].event = Event.MOTOR_BURNOUT
                    events["Motor burnout"] = sense_hat_data[-1].time
                elif row[9] == "Event.APOGEE":
                    sense_hat_data[-1].event = Event.APOGEE
                    events["Apogee"] = sense_hat_data[-1].time
                elif row[9] == "Event.TOUCH_DOWN":
                    sense_hat_data[-1].event = Event.TOUCH_DOWN
                    events["Touch Down"] = sense_hat_data[-1].time
                pitch.append(float(row[4]))
                roll.append(float(row[5]))
                yaw.append(float(row[6]))
    except Exception:
        print("rip")
base_pressure = (sense_hat_data[0].pressure + sense_hat_data[1].pressure + sense_hat_data[2].pressure + 
    sense_hat_data[3].pressure + sense_hat_data[4].pressure)/5
base_alt = pressure2alt(base_pressure)

t_sense = []
alt_sense = []
for data in sense_hat_data:
    t_sense.append(data.time)
    alt_sense.append((pressure2alt(data.pressure) - base_alt))

v_sense = [0.0]
for i in range(1, len(alt_sense)):
    v_sense.append((alt_sense[i] - alt_sense[i - 1])/(t_sense[i] - t_sense[i - 1]))

v_sense_smooth = []
for i in range(len(v_sense)):
    total = 0
    if i < 10:
        for j in range(i):
            total += v_sense[j]
        v_sense_smooth.append(total/(i + 1))
    else:
        for j in range(10):
            total += v_sense[i - j]
        v_sense_smooth.append(total/10)

t_strato1 = []
alt_strato1 = []
v_strato1 = []
with open("Alt1FlightData.csv", "r") as f:
    reader = csv.reader(f, delimiter=",")
    head = True
    for row in reader:
        if head:
            head = False
        else:
            t_strato1.append(float(row[0]))
            alt_strato1.append(feet2meter(float(row[1])))
            v_strato1.append(float(row[2]))

for i, angle in enumerate(pitch):
    pitch[i] = math.sin(angle/180*math.pi)

for i, angle in enumerate(roll):
    roll[i] = math.sin(angle/180*math.pi)

for i, angle in enumerate(yaw):
    yaw[i] = math.sin(angle/180*math.pi)

# Runge-Kutta
# 77 - 372

DIAMETER = inch2meter(6.188)
FIN_HEIGHT = inch2meter(12)
FIN_THICKNESS = inch2meter(0.25)
FIN_NUM = 4
ATS_FLAP_AREA = inch2meter(inch2meter(2.6336))
ATS_FLAP_NUM = 3
A = (DIAMETER ** 2)/4 + FIN_HEIGHT * FIN_THICKNESS * FIN_NUM
A_with_ATS = A + ATS_FLAP_AREA * ATS_FLAP_NUM
MASS = oz2kg(662)
Cd = 0.635
RHO = alt2rho(alt_sense[77] / 3.28084 + base_alt)

alt_pred_with_ATS = []
for i in range(372):
    v_n = v_sense[i]
    alt_n = alt_sense[i]
    t_n = t_sense[i]
    while (v_n >= 0):
        k1 = ode(STANDARD_GRAVITY, A_with_ATS, Cd, RHO, MASS, v_n)
        k2 = ode(STANDARD_GRAVITY, A_with_ATS, Cd, RHO, MASS, v_n + k1 * 0.5)
        k3 = ode(STANDARD_GRAVITY, A_with_ATS, Cd, RHO, MASS, v_n + k2 * 0.5)
        k4 = ode(STANDARD_GRAVITY, A_with_ATS, Cd, RHO, MASS, v_n + k3)
        v_n = v_n + STEP_SIZE * (k1 + 2.0 * k2 + 2.0 * k3 + k4)/6.0
        t_n += STEP_SIZE
        alt_n += STEP_SIZE * v_n
        RHO = alt2rho(alt_n + base_alt)
    alt_pred_with_ATS.append(alt_n)

alt_pred_smooth_with_ATS = []
for i in range(len(alt_pred_with_ATS)):
    total = 0
    if i < 10:
        alt_pred_smooth_with_ATS.append(alt_pred_with_ATS[i])
    else:
        for j in range(10):
            total += alt_pred_with_ATS[i - j]
        alt_pred_smooth_with_ATS.append(total/10)

alt_pred = []
for i in range(372):
    v_n = v_sense[i]
    alt_n = alt_sense[i]
    t_n = t_sense[i]
    while (v_n >= 0):
        k1 = ode(STANDARD_GRAVITY, A, Cd, RHO, MASS, v_n)
        k2 = ode(STANDARD_GRAVITY, A, Cd, RHO, MASS, v_n + k1 * 0.5)
        k3 = ode(STANDARD_GRAVITY, A, Cd, RHO, MASS, v_n + k2 * 0.5)
        k4 = ode(STANDARD_GRAVITY, A, Cd, RHO, MASS, v_n + k3)
        v_n = v_n + STEP_SIZE * (k1 + 2.0 * k2 + 2.0 * k3 + k4)/6.0
        t_n += STEP_SIZE
        alt_n += STEP_SIZE * v_n
        RHO = alt2rho(alt_n + base_alt)
    alt_pred.append(alt_n)

alt_pred_smooth = []
for i in range(len(alt_pred)):
    total = 0
    if i < 10:
        alt_pred_smooth.append(alt_pred[i])
    else:
        for j in range(10):
            total += alt_pred[i - j]
        alt_pred_smooth.append(total/10)

plt.figure(1)
plt.title("Altitude graph")
p1, = plt.plot(t_sense, alt_sense, color="r", label="SenseHAT altitude")
p2, = plt.plot(t_strato1, alt_strato1, color="b", label="Stratologger altitude")
plt.xlabel("time (s)")
plt.ylabel("altitude (m)")
plt.legend(handles=[p1, p2])

plt.figure(2)
plt.title("Velocity graph")
p3, = plt.plot(t_sense, v_sense, color="r", label="SenseHAT velocity")
p4, = plt.plot(t_strato1, v_strato1, color="b", label="Stratologger velocity")
p5, = plt.plot(t_sense, v_sense_smooth, color="g", label="SenseHAT velocity smoothed")
plt.xlabel("time (s)")
plt.ylabel("velocity (m/s)")
plt.legend(handles=[p3, p4, p5])

plt.figure(3)
plt.title("Rotation graph")
p6, = plt.plot(t_sense, pitch, color="r", label="Pitch")
p7, = plt.plot(t_sense, roll, color="b", label="roll")
p8, = plt.plot(t_sense, yaw, color="g", label="yaw")
plt.xlabel("time (s)")
plt.ylabel("Sine of angle")
plt.axvline(x=events["Apogee"], color="k", linestyle="-")
plt.legend(handles=[p6, p7, p8], bbox_to_anchor=(1,1), loc="upper left")
plt.tight_layout()

plt.figure(4)
plt.title("Altitude prediction")
p9, = plt.plot(t_sense, alt_sense, color="r", label="Actual Altitude")
p10, = plt.plot(t_sense[:372], alt_pred_smooth, color="b", label="Predicted Altitude without ATS")
p11, = plt.plot(t_sense[:372], alt_pred_smooth_with_ATS, color="g", label="Predicted Altitude Smoothed with ATS")
plt.xlabel("time (s)")
plt.ylabel("Altitude (m)")
p12 = plt.axhline(y=feet2meter(4800), color="k", linestyle="-", label="Target Apogee Altitude")
plt.axhline(y=feet2meter(4800 + 10), color="k", linestyle="dotted")
plt.axhline(y=feet2meter(4800 - 10), color="k", linestyle="dotted")
plt.legend(handles=[p9, p10, p11, p12])


plt.show()