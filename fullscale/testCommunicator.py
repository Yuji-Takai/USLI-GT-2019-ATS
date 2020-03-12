from communicator import Communicator
import time

def test():
    com = Communicator()
    while True:
        com.send("OK")
        time.sleep(1)


if __name__ == "__main__":
    test()