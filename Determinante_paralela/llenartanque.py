from multiprocessing import Process, Value, Array
from multiprocessing import Lock
import time
import os

def llenartanque(i,c,a,lista,lock):
    while(True):
        time.sleep(0.01)
        lock.acquire()
        if (a.value<c.value):            
            a.value+=1
            lista[i]=a.value
            lock.release()
        else:
            lock.release()
            break        

if __name__ == "__main__":
    num_processes = os.cpu_count()
    print("cantidad Procesadores:",num_processes)
    capacidadtanque = Value('i', 100)    
    actual = Value('i', 0)
    print("Medida inicial del tanque :",actual.value)
    lock = Lock()
    processes = []    
    cuantollenado =  Array('d', [0 for _ in range(num_processes)])
    
    # number of CPUs on the machine. Usually a good choise for the number of processes

    # create processes and asign a function for each process
    for i in range(num_processes):
        process = Process(target=llenartanque,args=(i,capacidadtanque,actual,cuantollenado, lock,))
        processes.append(process)

    # start all processes
    for process in processes:
        process.start()

    # wait for all processes to finish
    # block the main programm until these processes are finished
    for process in processes:
        process.join()
    print("Medida final del tanque :",actual.value)    
    print(cuantollenado[:])
    print([((i+1),item)for i,item in enumerate(cuantollenado) if item==capacidadtanque.value ])
