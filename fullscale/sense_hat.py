import csv

class SenseHat:

    def __init__(self):
        self.count_acceler = 0
        self.count_orient = 0
        self.count_temp = 0
        self.count_pressure = 0
        self.count_humidity = 0
        self.file = "./data_only_launch.csv"
        self.acceler = []
        self.orientation = []
        self.temp = []
        self.pressure = []
        self.humidity = []
        self.readcsv()


    def readcsv(self):
        with open(self.file, "r") as f:
            csv_reader = csv.reader(f)
            head = True
            for row in csv_reader:
                if head:
                    head = False
                else:
                    self.acceler.append(dict(x=float(row[1]), y=float(row[2]), z=float(row[3])))
                    self.orientation.append(dict(pitch=float(row[4]), roll=float(row[5]), yaw=float(row[6])))
                    self.temp.append(float(row[7]))
                    self.pressure.append(float(row[8]))
                    self.humidity.append(float(row[9]))


    def get_accelerometer_raw(self):
        if self.count_acceler < len(self.acceler):
            val = self.acceler[self.count_acceler]
            self.count_acceler += 1
            return val

        return self.acceler[-1]

    def get_orientation(self):
        if self.count_orient < len(self.orientation):
            val = self.orientation[self.count_orient]
            self.count_orient += 1
            return val
        return self.orientation[-1]

    def get_temperature(self):
        if self.count_temp < len(self.temp):
            val = self.temp[self.count_temp]
            self.count_temp += 1
            return val
        return self.temp[-1]

    def get_pressure(self):
        if self.count_pressure < len(self.pressure):
            val = self.pressure[self.count_pressure]
            self.count_pressure += 1
            return val
        return self.pressure[-1]

    def get_humidity(self):
        if self.count_humidity < len(self.humidity):
            val = self.humidity[self.count_humidity]
            self.count_humidity += 1
            return val
        return self.humidity[-1]
