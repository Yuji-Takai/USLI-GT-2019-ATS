class CircularQueue:
    '''
    Represents a circular queue
    The circular queue is implemented in a LRU fashion, so the least 
    recently used data is deleted from the circular queue.

    capacity : int
        the capacity of the circular queue
    back_arr : list
        the backing array of the circular queue
    back_size : int
        the size of the backing array of the circular queue
    add_index : int
        the index at which new data will be added onto the backing array 
    '''
    def __init__(self, capacity):
        self.capacity = capacity
        self.back_arr = [None] * self.capacity
        self.back_size = 0
        self.add_index = 0

    def __str__(self):
        '''
        Returns the string representation of backing array in correct order
        '''
        return str(self.toArray())

    def size(self):
        '''
        Returns the size of the backing array
        '''
        return self.back_size

    def get(self, index):
        '''
        Returns the index-th most recent data from the backing array
        '''
        return self.back_arr[(self.add_index + index) % self.capacity]

    def add(self, data):
        '''
        Adds the data to the backing array in a LRU fashion
        '''
        self.back_arr[self.add_index] = data
        self.add_index = (self.add_index + 1) % self.capacity
        self.back_size = self.back_size + 1 if self.back_size < self.capacity else self.capacity

    def toArray(self):
        '''
        Returns the backing array so that it is in the right order i.e. index 0 has the least recent value
        '''
        arr = []
        for i in range(self.back_size):
            arr.append(self.back_arr[(self.add_index + i) % self.capacity])
        return arr

    def average(self):
        '''
        Returns the average value of the backing array 
        [NOTE] use it only when the circular queue stores int or float
        '''
        total = 0.0
        for i in range(self.back_size):
            total += self.back_arr[i]
        return total/self.back_size


    def get_last(self):
        '''
        Returns the most recent data from the backing array
        '''
        return self.back_arr[(self.add_index + self.capacity - 1) % self.capacity] if self.back_size > 0 else None

    def get_second_last(self):
        '''
        Returns the second most recent data from the backing array
        '''
        return self.back_arr[(self.add_index + self.capacity - 2) % self.capacity] if self.back_size > 1 else None