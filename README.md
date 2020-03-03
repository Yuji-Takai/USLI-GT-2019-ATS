# USLI-GT-2019-ATS
## Description
Apogee Targeting System (ATS) is a drag inducing system which allows the launch vehicle to approach our team's target apogee altitude for NASA USLI competition. This repository stores the source code of the software of ATS 2019 - 2020 version. 

## Contributors
+ Yuji Takai 
+ Alexander Puckhaber

## Subscale
`subscale` contains `logger.py`, the logger file that was run on the first and second subscale flights in 2019. The main functionality implemented were logging the Sense HAT data and actuating the flaps after few seconds from launch. The acceleration value, which was used for detecting launch, maxed out, causing the detection logic to fail and the flaps did not actually actuate for subscale

## Fullscale
`fullscale` contains all parts of the fullscale version of the ATS software. The software is implemented as a finite state machine. Please refer to the image below for the details of the state machine.
![Image of FSM](https://github.com/Yuji-Takai/USLI-GT-2019-ATS/blob/master/img/FSM-fullscale-ATS.png)