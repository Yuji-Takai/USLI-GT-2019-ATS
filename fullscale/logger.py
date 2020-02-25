class Logger:
    def __init__(self, fname):
        self.buffer = []
        self.fname = fname

    def initLogFile(self):
        with open(self.fname, 'w') as f:
            f.write("{},{},{},{},{},{},{},{},{},{}".format("time", "ax",
                "ay", "ax", "pitch", "roll", "yaw", "temperature", "pressure",
                "event"))

    def write(self, data, length_threshold=20):
        self.buffer.append(data)
        if len(self.buffer) == length_threshold:
            with open(self.fname, 'a') as f:
                for x in self.buffer:
                    f.write("{}\n".format(str(x)))
            self.buffer = []

    def purge(self):
        with open(self.fname, 'a') as f:
            for x in self.buffer:
                f.write("{}\n".format(str(x)))
        self.buffer = []