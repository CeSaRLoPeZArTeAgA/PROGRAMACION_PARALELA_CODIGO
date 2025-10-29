from multiprocessing import Process, Value, Array
import time

def add_100(number):
    for _ in range(100):
        time.sleep(0.01)
        number.value += 1

def add_100x(number):
    for _ in range(100):
        time.sleep(0.01)
        number.value += 1

def add_100_array(numbers):
    for _ in range(100):
        time.sleep(0.01)
        for i in range(len(numbers)):
            numbers[i] += 1

if __name__ == "__main__":
    # i = 0
    shared_number = Value('i', 0) 
    shared_numberj = Value('i', 0) 
    print('Value at beginning:', shared_number.value)
    # d = [0.0, 100.0, 200.0]
    shared_array = Array('d', [0.0, 100.0, 200.0])
    print('Array at beginning:', shared_array[:])

    process1 = Process(target=add_100, args=(shared_number,))
    process2 = Process(target=add_100x, args=(shared_numberj,))

    process3 = Process(target=add_100_array, args=(shared_array,))
    process4 = Process(target=add_100_array, args=(shared_array,))

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
