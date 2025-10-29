# EN ESTA CODIGO SE CREA LOS HILOS, ENTENDER QUE EL MAIN TAMBIEN ES UN HILO.
# AQUI LOS HILOS HACEN SU PROCESO Y SE ESPERAN ENTRE ELLOS(join), PERO SIN SALIR
# DEL MAIN. UNA VEZ CULMINADO LA TAREA DE CADA HILO, RECIEN TERMINA EL HILO
# DEL MAIN

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

# esperamos a que terminen los hilos
hilo1.join()
hilo2.join()

print('El hilo principal sí espera por el resto de hilos.')