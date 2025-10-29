# MANEJO DE HILOS, EN ESTA SE CREA LOS HILOS, PERO EL MAIN SE CONSIDERA
# COMO UN HILO MAS Y ESTE SE EJECUTA ANTES QUE TERMINEN LOS HILOS CREADOS DENTRO DE ELLA
import threading
from time import sleep
import random


def ejecutar():
    print(f'Comienza {threading.current_thread().name}')
    sleep(random.random())  # esperamos un tiempo aleatorio entre 0 y 1 segundos
    print(f'Termina {threading.current_thread().name}')


# creamos los hilos
hilo1 = threading.Thread(target=ejecutar, name='Hilo 1')
hilo2 = threading.Thread(target=ejecutar, name='Hilo 2')

# ejecutamos los hilos
hilo1.start()
hilo2.start()

print('El hilo principal no espera por el resto de hilos.')