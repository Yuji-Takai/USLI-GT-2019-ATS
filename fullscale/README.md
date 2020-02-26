# ATS Fullscale Software

## Structure
```
.
├── README.md
├── actuator.py 
├── ats_math.py
├── calculator.py
├── circular_queue.py
├── communicator.py
├── constants.py
├── data_only_launch.csv
├── event.py
├── logger.py
├── main.py
├── rocket.py
├── sense_hat.py
├── sensor.py
└── sensor_data.py
```

## Execution
For subscale mode run:
```
python main.py -s
```
For fullscale mode run:
```
python main.py -f
```

## To-Do List
+ base altitude should use average pressure before launch
+ find a good way to smooth the velocity data
    - find a way to best fit the altitude data so that the velocity values will be better
+ `Actuator.actuate()` function should intake a degree of actuation instead simply fully actuating the flaps
+ Cd calculation should be done as the launch vehicle flies