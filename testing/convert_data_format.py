import pandas as pd
import datetime
import numpy as np

flight1_df = pd.read_csv('flight1.csv')



def my_converter(str):
    return datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S.%f')

datatime_func_vectorized = np.vectorize(my_converter)

new_time = datetime.datetime.strptime('2019-11-14 20:33:51.303329', '%Y-%m-%d %H:%M:%S.%f')

flight1_df['new_time'] = datatime_func_vectorized(flight1_df['time'])



flight1_df['new_time'] -= flight1_df['new_time'][0]

flight1_df['new_time'] = flight1_df['new_time'].dt.total_seconds()

print(flight1_df)

new_df = pd.DataFrame(columns=['time', 'ax', 'ay', 'az', 'pitch', 'roll', 'yaw', 'temperature', 'pressure', 'event'])

new_df['time'] = flight1_df['new_time']
new_df['az'] = -flight1_df['accel_x']   # negative because of reversed direction
# for x and z, not really paying attention to accel direction :/
new_df['ax'] = flight1_df['accel_y']
new_df['ay'] = flight1_df['accel_z']

new_df['pressure'] = flight1_df['pressure']
new_df['roll'] = flight1_df['roll']
new_df['pitch'] = flight1_df['pitch']
new_df['yaw'] = flight1_df['yaw']
new_df['temperature'] = flight1_df['temperature']
new_df['event'] = flight1_df['markers']

print(new_df)

new_df.to_csv('subscale_flight1.csv', index=False)