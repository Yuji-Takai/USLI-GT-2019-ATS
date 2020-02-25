class CircularQueue:
    def __init__(self, capacity):
        self.capacity = capacity
        self.back_arr = [None] * self.capacity
        self.back_size = 0
        self.add_index = 0

    def __str__(self):
        return str(self.toArray())

    def size(self):
        return self.back_size

    def get(self, index):
        return self.back_arr[(self.add_index + index) % self.capacity]

    def add(self, data):
        self.back_arr[self.add_index] = data
        self.add_index = (self.add_index + 1) % self.capacity
        self.back_size = self.back_size + 1 if self.back_size < self.capacity else self.capacity

    def toArray(self):
        arr = []
        for i in range(self.back_size):
            arr.append(self.back_arr[(self.add_index + i) % self.capacity])
        return arr

    def average(self):
        total = 0.0
        for i in range(self.back_size):
            total += self.back_arr[i]
        return total/self.back_size


    def get_last(self):
        return self.back_arr[(self.add_index + self.capacity - 1) % self.capacity] if self.back_size > 0 else None

    def get_second_last(self):
        return self.back_arr[(self.add_index + self.capacity - 2) % self.capacity] if self.back_size > 1 else None