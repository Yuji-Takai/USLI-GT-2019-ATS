class StratoLoggerData():
    '''
    Represents the data retrieved from StratoLogger CF
    
    time: float
        time from take off in seconds
    alt: float
        altitude in feet
    v: float
        vertical velocity in ft/s
    temp: float
        surrounding temperature in C
    voltage: float
        battery voltage in V
    '''
    def __init__(self, time, alt, v, temp, voltage):
        self.time = time 
        self.alt = alt
        self.v = v
        self.temp = temp
        self.voltage = voltage
