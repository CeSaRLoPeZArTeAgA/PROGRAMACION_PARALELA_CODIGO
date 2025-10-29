from multiprocessing import Process
import os
global cadena
cadena = "Hola"
def square_numbers():
    global cadena
    for i in range(1000):
        result = i * i
    cadena = cadena +str(i)
    print(cadena)

if __name__ == "__main__":        
    processes = []
    num_processes = os.cpu_count()
    # number of CPUs on the machine. Usually a good choise for the number of processes

    # create processes and asign a function for each process
    for i in range(num_processes):
        process = Process(target=square_numbers)
        processes.append(process)
        print("proceso:",num_processes)

    # start all processes
    for process in processes:
        process.start()

    # wait for all processes to finish
    # block the main programm until these processes are finished
    for process in processes:
        process.join()
    
    print(cadena)
