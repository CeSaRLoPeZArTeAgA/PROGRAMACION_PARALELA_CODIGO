import time
import tkinter as tk
import threading
from tkinter import simpledialog
from tkinter import *
from tkinter.ttk import *


# pedimos cantidad de hilos
def obtener_dato():
    # Mostrar un cuadro de diálogo para pedir datos inicial
    n = int(simpledialog.askstring("Entrada de datos", "Ingrese numero de hilos: \t\t\t "))
    return n
# Ventana principal
window = Tk()
window.withdraw()  # ocultamos hasta que se tenga el dato
n = obtener_dato()
window.deiconify()  # mostramos de nuevo

# Listas dinámicas
velocidades = [0 for _ in range(n)]
recorridos = ["|" for _ in range(n)]
hilos = [None for _ in range(n)]
labels_velocidad = []
labels_carro = []

#window = Tk()
window.title(f"Paralelismo: {n} - hilos")
window.geometry('800x300')

# Función del hilo
def recorriendo(idhilo):
    global recorridos
    while len(recorridos[idhilo]) < 150:
        recorridos[idhilo] += "|" * velocidades[idhilo]
        labels_carro[idhilo].configure(
            text=recorridos[idhilo] + " " * (150 - len(recorridos[idhilo]))
        )
        time.sleep(1)

# funciones de control
def acelerar(idhilo):
    global hilos
    if hilos[idhilo]:
        if velocidades[idhilo] < 5:
            velocidades[idhilo] += 1
            labels_velocidad[idhilo].configure(text=str(velocidades[idhilo]))
    else:
        print(f"Hilo {idhilo+1} creado")
        hilos[idhilo] = threading.Thread(target=recorriendo, args=(idhilo,))
        hilos[idhilo].start()

def desacelerar(idhilo):
    if velocidades[idhilo] > 0:
        velocidades[idhilo] -= 1
        labels_velocidad[idhilo].configure(text=str(velocidades[idhilo]))

# creacion dinamica de interfaz
for i in range(n):
    # Botón acelerar
    btn_acel = Button(window, text=f"Acelerar {i+1}", command=lambda i=i: acelerar(i))
    btn_acel.grid(column=0, row=i)

    # Botón desacelerar
    btn_desacel = Button(window, text=f"Desacelerar {i+1}", command=lambda i=i: desacelerar(i))
    btn_desacel.grid(column=1, row=i)

    # Velocidad
    lblv = Label(window, text=str(velocidades[i]))
    lblv.grid(column=2, row=i)
    labels_velocidad.append(lblv)

    # Carro (recorrido)
    lblcarro = Label(window, text=" " * 150)
    lblcarro.grid(column=3, row=i)
    labels_carro.append(lblcarro)


window.mainloop()
