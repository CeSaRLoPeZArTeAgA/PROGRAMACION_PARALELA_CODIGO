# Implementar el Fibonacci para la funcionalidad en procesos.
from multiprocessing import Process, Value, Array
import time
import os
####
def fibonacciR(n):
    #init = time.time()
    if n <= 1:
        return n
    return fibonacciR(n - 1) + fibonacciR(n - 2)

def recursivo(n):
    return fibonacciR(n)
#####    

if __name__ == "__main__":   
    init = time.time() 
    #n = 40 #fibonacci de n =     
    processes = []
    shared_number = Value('i', 0) 
    shared_number=40
    num_processes = os.cpu_count()
    # number of CPUs on the machine. Usually a good choise for the number of processes

    # create processes and asign a function for each process
    for i in range(num_processes):
        process = Process(target=recursivo, args=(shared_number,))
        processes.append(process)
        print("proceso:",i)

    # start all processes
    for process in processes:
        process.start()

    # wait for all processes to finish
    # block the main programm until these processes are finished
    for process in processes:
        process.join()
    tSerial = time.time() - init
    
    print("\nRESUMEN DE RESULTADOS")
    print('Tiempo serial es: '+str(tSerial))
    print(f"Numero de procesadores trabajados:{num_processes}")
    print(f"Numeros de terminos para la serie de fibonacci es: {shared_number}")
    print("Fin de procesos .....")
