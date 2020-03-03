class Logger:
    '''
    Represents the logger 
    The logger buffers some of the data before writing to the log file for improving performance

    buffer : list
        buffer that stores the sensor data in a temporary manner
    fname : str
        name of the logger file
    '''
    def __init__(self, fname):
        self.buffer = []
        self.fname = fname
        self.initLogFile()

    def initLogFile(self):
        '''
        initialize the log file by adding headers
        '''
        with open(self.fname, 'w') as f:
            f.write("{},{},{},{},{},{},{},{},{},{}\n".format("time", "ax",
                "ay", "ax", "pitch", "roll", "yaw", "temperature", "pressure",
                "event"))

    def write(self, data, length_threshold=20):
        '''
        writes to the logger file only when the buffer size reaches the threshold
        '''
        self.buffer.append(data)
        if len(self.buffer) == length_threshold:
            with open(self.fname, 'a') as f:
                for x in self.buffer:
                    f.write("{}\n".format(str(x)))
            self.buffer = []

    def purge(self):
        '''
        writes to the logger file from the buffer
        need this function because when the launch vehicle lands, the buffer might not be full to be written 
        '''
        with open(self.fname, 'a') as f:
            for x in self.buffer:
                f.write("{}\n".format(str(x)))
        self.buffer = []