# PC 1 - Pregunta 3 - CLA

import threading
import time
import os
from datetime import datetime

# variables compartidas, los cuales son globales
tanque = 0
resultado = -1
lock = threading.Lock()

def llenarT(thread_id):
    global tanque, resultado
    while True:
        with lock:
            if tanque >= 100:
                # salir si el tanque esta lleno
                break
            tanque += 1
            resultado = thread_id
            print(f"Hilo {thread_id} lleno ---> {tanque} litro")
        # simular tiempo de llenado
        time.sleep(0.01)

if __name__ == "__main__":
    
    # numero de hilos a crear sera igual al numero procesadores disponibles
    num_hilos = os.cpu_count()   

    # variable para control de tiempo
    init = time.time()

    print(f"\nHISTORIAL LLENADO TANQUE X HILO - {datetime.now()}\n")

    hilos = []
    for i in range(num_hilos):
        t = threading.Thread(target=llenarT, args=(i,))
        hilos.append(t)
        t.start()

    for t in hilos:
        t.join()

    tFinal = time.time() - init

    print(f"\n--------  RESUMEN DE LLENADO TANQUE (HILOS) ---------")
    print(f"Numero de hilos(CPU): {num_hilos}")
    print(f"Tiempo total de llenado Tanque: {tFinal:.4f} segundos")
    print(f"Tanque lleno con {tanque} litros")
    print(f"Ultimo Hilo que lleno el tanque: {resultado}\n")
