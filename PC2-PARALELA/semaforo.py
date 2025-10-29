import threading
import time
import math
import random
import serial

arduino = serial.Serial('COM5', 9600)  
time.sleep(2) 

#variables de modelo gaussiando
PERIODO_GAUSS = 300.0  # 5 minutos = 300 segundos
SIGMA = 50.0
MU = PERIODO_GAUSS / 2

# Variables
extra_verde = 0.0  # minutos adicionales al color verde
extra_rojo = 0.0   # minutos adicionales al colo rojo
lock = threading.Lock()      # Para sincronizar variables
serial_lock = threading.Lock()  # Para proteger la escritura serial


#funcion trafico (gaussiano) ---
def Trafico():
    global extra_verde
    t0 = time.time()
    while True:
        t = (time.time() - t0) % PERIODO_GAUSS
        
        # funcion gaussiana normalizada [0,1]
        f = math.exp(-((t - MU) ** 2) / (2 * SIGMA ** 2))
        
        # escala el tiempo extra en minutos
        incremento = f * 1.0  # hasta +1 min
        
        with lock:
            extra_verde = incremento
        
        # enviando al arduino - bloque enviado protegido
        with serial_lock:
            try:
                mensaje = f"V:{incremento:.2f}\n"
                arduino.write(mensaje.encode())
            except serial.SerialTimeoutException:
                print("Error: al enviar tráfico el tiempo al arduino")
        
        #impresion por la shell de python
        print(f"[Tráfico] f={f:.2f}, extra verde = {incremento:.2f} min")
        time.sleep(5)  # actualizar cada 5 segundos

#funcion que indica la llegada de una ambulancia
def Ambulancia():
    global extra_rojo
    while True:
        valor = random.random()  # [0,1)
        if valor < 0.01:  # llega ambulancia
            with lock:
                extra_rojo = 1.0
            mensaje = "R:1\n"
            #impresion por la shell de python
            print("[Ambulancia] Extiende rojo + 1 min")
        else:
            with lock:
                extra_rojo = 0.0
            mensaje = "R:0\n"
            
        # enviando al arduino - bloque enviado protegido
        with serial_lock:
            try:
                arduino.write(mensaje.encode())
            except serial.SerialTimeoutException:
                print("Error: al enviar el tiempo de la ambulancia")

        time.sleep(10)  # verificar cada 10 s

#hilo para el trafico, mas tiempo en color verde
t1 = threading.Thread(target=Trafico, daemon=True)
#hilo para el paso de una ambulancia, mas tiempo en color rojo
t2 = threading.Thread(target=Ambulancia, daemon=True)

#inicializando hilos
t1.start()
t2.start()

print("Sistema paralelo iniciado (Ctrl+C para detener)")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Finalizando...")
    arduino.close()
