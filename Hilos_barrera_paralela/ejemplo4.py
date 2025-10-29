# SE CREA HILOS, PERO AL MOMENTO DE ACCEDER AL RECURSO DE FICHERO, ESTA DEBERA SER UNO A UNO
# PARA ESO SE BLOQUE EL RECURSO(lock) MIENTRAS UN HILO ESTA TRABAJANDO EN ELLA Y LO APERTURA
# APENAS TERMINEN DESBLOQUEA 

import threading
import random

def escribir_valor(autor, valor):
    lock_acceso_fichero.acquire()  # pedimos acceso al recurso
    with open('resultados.txt', 'a') as fichero:  # abrimos el fichero para añadir contenido al final
        fichero.write(f'{autor} - {valor}\n')
    lock_acceso_fichero.release()  # liberamos el recurso en cuanto terminamos con él


def ejecutar():
    valor = sum([random.random() for i in range(0, random.randint(1, 1000))])  # generamos 100 números aleatorios entre 0 y 1 y los sumamos
    escribir_valor(threading.current_thread().name, valor)


# creamos los hilos
hilo1 = threading.Thread(target=ejecutar, name='Hilo 1')
hilo2 = threading.Thread(target=ejecutar, name='Hilo 2')
hilo3 = threading.Thread(target=ejecutar, name='Hilo 3')

# creamos el Lock
lock_acceso_fichero = threading.Lock()

# ejecutamos los hilos
hilo1.start()
hilo2.start()
hilo3.start()