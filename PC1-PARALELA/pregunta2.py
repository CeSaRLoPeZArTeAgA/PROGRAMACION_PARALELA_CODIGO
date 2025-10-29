# PC 1 - Pregunta 2 - CLA
import multiprocessing
import time
from datetime import datetime

def llenarT(tanque, lock, resultado, proc_id):
    # en esta parte asegura que solo un proceso a la vez pueda modificar el volumen del tanque
    while True:
        with lock:
            if tanque.value >= 100:
                # salir de la secuencia si el tanque esta lleno
                break
            tanque.value += 1
            # Guardamos el id del proceso que lleno el ultimo litro.
            # al final este recurso sera invocado para ver quien 
            # lleno el final del tanque
            resultado.value = proc_id
            print(f"Proceso {proc_id} lleno ---> {tanque.value} litro")
        # Simular tiempo de llenado
        time.sleep(0.01)

if __name__ == "__main__":
    
    # Variable compartida para la cantidad de litros en el tanque
    shared_tanque = multiprocessing.Value('i', 0)
    
    # Variable compartida para guardar el id del proceso que lleno el tanque
    resultado = multiprocessing.Value('i', -1)
    
    # Lock para sincronizar acceso al tanque
    lock = multiprocessing.Lock()

    # Número de procesadores disponibles
    num_procesadores = multiprocessing.cpu_count()

    #variable para control de tiempo
    init = time.time() 
    
    #hace el arreglo de procesos que intervendran en el llenado (la cantidad es en funcion del CPU que se tiene)
    print(f"\nHISTORIAL LLENADO TANQUE X PROCESO - {datetime.now()}\n")
    procesos = []
    for i in range(num_procesadores):
        p = multiprocessing.Process(target=llenarT, args=(shared_tanque, lock, resultado, i))
        procesos.append(p)
        p.start()

    #espera que todos los procesos terminen en el llenado para pasar a listar la parte final
    for p in procesos:
        p.join()
        
    # tiempo final para todos los procesos
    tFinal = time.time() - init

    # impresion de los resultados finales
    print(f"\n--------  RESUMEN DE LLENADO TANQUE  ---------")
    print(f"Numero de procesadores: {num_procesadores}")
    print(f"Tiempo total de llenado Tanque: {tFinal:.4f} segundos")
    print(f"Tanque lleno con {shared_tanque.value} litros")
    print(f"Ultimo Proceso que lleno el tanque: {resultado.value}\n")