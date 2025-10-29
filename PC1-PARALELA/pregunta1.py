# PC 1 - Pregunta 1 - CLA
import threading
import time
from tkinter import *
from tkinter.ttk import *

window = Tk()
window.title("Pregunta 1: Diferencia entre Carros - CLA")
window.geometry('650x300')

# variables globales
velocidad1, velocidad2 = 0, 0
recorrido1, recorrido2 = "|", "|"

# etiquetas de velocidad y recorrido de los vehículos
lblv1 = Label(window, text=str(velocidad1))
lblv1.grid(column=3, row=0)

lblcarro1 = Label(window, text=" " * 150)
lblcarro1.grid(column=4, row=0)

lblv2 = Label(window, text=str(velocidad2))
lblv2.grid(column=3, row=1)

lblcarro2 = Label(window, text=" " * 150)
lblcarro2.grid(column=4, row=1)

# Etiqueta para mostrar la diferencia de distancia
lbletiqueta = Label(window, text="Distancia entre carros:")#sollo es etiqueta fija
lbletiqueta.grid(column=0, row=7,sticky='w')
lbldiferencia = Label(window, text="-")
lbldiferencia.grid(column=3, row=7, columnspan=2, sticky='w')

# Hilos
hilo1 = None
hilo2 = None
hilo_diferencia = None

# Función para el recorrido de cada vehículo
def recorriendo(idhilo):
    global velocidad1, velocidad2, recorrido1, recorrido2
    if idhilo == 1:
        while len(recorrido1) < 150:
            recorrido1 = recorrido1 + "|" * velocidad1
            lblcarro1.configure(text=str(recorrido1 + " " * (150 - len(recorrido1))))
            time.sleep(1)
    elif idhilo == 2:
        while len(recorrido2) < 150:
            recorrido2 = recorrido2 + "|" * velocidad2
            lblcarro2.configure(text=str(recorrido2 + " " * (150 - len(recorrido2))))
            time.sleep(1)

# Funciones de aceleración y desaceleración
def acelerar1():
    global hilo1, velocidad1
    if hilo1 is None:
        hilo1 = threading.Thread(target=recorriendo, args=(1,))
        hilo1.start()
    if velocidad1 < 5:
        velocidad1 += 1
        lblv1.configure(text=str(velocidad1)) 

def desacelerar1():
    global velocidad1
    if velocidad1 > 0:
        velocidad1 -= 1
        lblv1.configure(text=str(velocidad1))

def acelerar2():
    global hilo2, velocidad2
    if hilo2 is None:
        hilo2 = threading.Thread(target=recorriendo, args=(2,))
        hilo2.start()
    if velocidad2 < 5:
        velocidad2 += 1
        lblv2.configure(text=str(velocidad2))

def desacelerar2():
    global velocidad2
    if velocidad2 > 0:
        velocidad2 -= 1
        lblv2.configure(text=str(velocidad2))

# Función para calcular la diferencia de distancia
def calcular_diferencia():
    global recorrido1, recorrido2
    while True:
        diferenciaCarros = abs(len(recorrido1) - len(recorrido2))
        lbldiferencia.configure(text=f"{'|' * diferenciaCarros}")
        time.sleep(1)

# Botones de aceleración y desaceleración
btnacelerar1 = Button(window, text="Acelerar1", command=acelerar1)
btnacelerar1.grid(column=1, row=0)

btndesacelerar1 = Button(window, text="Desacelerar1", command=desacelerar1)
btndesacelerar1.grid(column=0, row=0)

btnacelerar2 = Button(window, text="Acelerar2", command=acelerar2)
btnacelerar2.grid(column=1, row=1)

btndesacelerar2 = Button(window, text="Desacelerar2", command=desacelerar2)
btndesacelerar2.grid(column=0, row=1)

# Iniciar el hilo para calcular la diferencia de distancia
if hilo_diferencia is None:
    hilo_diferencia = threading.Thread(target=calcular_diferencia)
    hilo_diferencia.daemon = True  # El hilo termina cuando se cierra la aplicación
    hilo_diferencia.start()

window.mainloop()
