# import Lock
from multiprocessing import Lock
from multiprocessing import Process, Value, Array
import time

def add_100(number, lock):
    for _ in range(100):
        time.sleep(0.01)
        with lock:
            number.value += 1
            
def add_100xxx(number, lock):
    for _ in range(100):
        time.sleep(0.01)
        # lock the state
        lock.acquire()

        number.value += 1

        # unlock the state
        lock.release()

def add_100_array(numbers, lock):
    for _ in range(100):
        time.sleep(0.01)
        for i in range(len(numbers)):
            lock.acquire()
            numbers[i] += 1
            lock.release()

if __name__ == "__main__":

    # create a lock
    lock = Lock()

    shared_number = Value('i', 0) 
    print('Value at beginning:', shared_number.value)

    shared_array = Array('d', [0.0, 100.0, 200.0])
    print('Array at beginning:', shared_array[:])

    # pass the lock to the target function
    process1 = Process(target=add_100, args=(shared_number, lock))
    process2 = Process(target=add_100, args=(shared_number, lock))

    process3 = Process(target=add_100_array, args=(shared_array, lock))
    process4 = Process(target=add_100_array, args=(shared_array, lock))

    process1.start()
    process2.start()
    process3.start()
    process4.start()

    process1.join()
    process2.join()
    process3.join()
    process4.join()

    print('Value at end:', shared_number.value)
    print('Array at end:', shared_array[:])

    print('end main')
