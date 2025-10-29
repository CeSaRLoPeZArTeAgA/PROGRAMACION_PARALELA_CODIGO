
from multiprocessing import Process, Manager, Value
import time

def fibonacciR(n):
    if n <= 1:
        return n
    return fibonacciR(n - 1) + fibonacciR(n - 2)

def add_fibo(shared_list, n):
    # ya tenemos los primeros dos términos
    for i in range(2, n):
        fn = fibonacciR(i)
        shared_list.append(fn)

if __name__ == "__main__":
    init = time.time() 
    # valor compartido
    shared_numberF = Value('i', 40)
    
    # lista compartida administrada
    with Manager() as manager:
        shared_list = manager.list([0, 1])  # primeros dos términos
        
        # crear procesos
        p1 = Process(target=add_fibo, args=(shared_list, shared_numberF.value))
        p2 = Process(target=add_fibo, args=(shared_list, shared_numberF.value))
        
        p1.start()
        p2.start()
        
        p1.join()
        p2.join()
        
        
        print(f"Valor de términos: {shared_numberF.value}")
        print("Array final:", list(shared_list))
        print("end main")
    
    tSerial = time.time() - init
    
    print("\nRESUMEN DE RESULTADOS")
    print('Tiempo serial es: '+str(tSerial))
    #print(f"Numero de procesadores trabajados:{num_processes}")
    #print(f"Numeros de terminos para la serie de fibonacci es: {shared_numberF}")
    print("Fin de procesos .....")


