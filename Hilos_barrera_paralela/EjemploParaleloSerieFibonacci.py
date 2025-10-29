import time
import numpy as np
import matplotlib.pyplot as plt
from threading import Thread
from multiprocessing import Process,cpu_count
def fibonacciR(n):
    if n <= 1:
        return n
    return fibonacciR(n - 1) + fibonacciR(n - 2)
    
def recursivo(n):
    return fibonacciR(n)
    
if __name__ == '__main__':
    print("Cantidad de procesadores:",cpu_count())
    n = 40 #fibonacci de n = 
    veces = cpu_count()# veces que se va a repetir
    # -------- SERIAL
    TSerial = []
    for _ in range(veces):
        init = time.time()
        for i in range(veces):        
            recursivo(n)   
        tSerial = time.time() - init
        print('Tiempo serial con '+str(n) + ' es: '+str(tSerial))
        TSerial.append(tSerial)
    
    # -------- PARALELO
    TParalelo = []
    hilos = {}
    for _ in range(veces):
        init = time.time()
        for i in range(veces):        
            hilos[i] = Thread(target=recursivo,kwargs={'n':n})
            hilos[i].start()
            
        """
        while(len(hilos) > 0):
            i = len(hilos)
            if not hilos[i].is_alive():
                del hilos[i]
        """                
        tParalelo = time.time() - init
        TParalelo.append(tParalelo)
        print('Tiempo paralelo con '+str(n) + ' es: '+str(tParalelo))
    
    fig, ax = plt.subplots()
    ax.plot(np.arange(len(TSerial)), np.array(TSerial), label='Serial')
    ax.plot(np.arange(len(TParalelo)), np.array(TParalelo), label='Paralelo')
    plt.legend()
    ax.set_xlabel("n")
    ax.set_ylabel("Time (seconds)")
    plt.show() 
