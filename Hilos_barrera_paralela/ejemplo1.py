# CREACION DE HILOS - BASICO
import threading


def info():
    print(f'{threading.current_thread().name} {threading.get_native_id()}')


# creamos los hilos
hilo1 = threading.Thread(target=info)
hilo2 = threading.Thread(target=info)
hilo3 = threading.Thread(target=info)

# ejecutamos los hilos
hilo1.start()
hilo2.start()
hilo3.start()


# el programa principal sigue ejecutándose aunque los hilos no hayan terminado
print(f'{threading.current_thread().name} {threading.get_native_id()}')