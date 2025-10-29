import threading
import time
from tkinter import *
from tkinter.ttk import *
window = Tk()
window.title("Hilos")
window.geometry('650x300')
global velocidad1
velocidad1,velocidad2 = 0,0
recorrido1,recorrido2 = "|","|"
lblv1 = Label(window,text=str(velocidad1))
lblv1.grid(column=3,row=0)

lblcarro1 = Label(window,text=" "*150)
lblcarro1.grid(column=4,row=0)

hilo1 = None

def recorriendo(idhilo):
    if idhilo==1:        
        global velocidad1
        global recorrido1
        global hilo1
        while len(recorrido1)<150:
            recorrido1 = recorrido1 + "|"*velocidad1
            lblcarro1.configure(text=str(recorrido1 + " "*(150-len(recorrido1))))
            time.sleep(1)
            
    if idhilo==2:        
        global velocidad2
        global recorrido2
        global hilo2
        while len(recorrido2)<150:
            recorrido2 = recorrido2 + "|"*velocidad2
            lblcarro2.configure(text=str(recorrido2 + " "*(150-len(recorrido2))))
            time.sleep(1)
    
def acelerar1():
    global hilo1
    if hilo1:
        global velocidad1
        if velocidad1<5:
            velocidad1 = velocidad1 + 1
            lblv1.configure(text=str(velocidad1))
    else:
        print("Hilo 1 creado")
        hilo1 = threading.Thread(target=recorriendo, args=(1,))
        # Inicia el Hilo
        hilo1.start()
        
def desacelerar1():
    global velocidad1
    if velocidad1 >0:
        velocidad1 = velocidad1 - 1
        lblv1.configure(text=str(velocidad1))
    
btnacelerar1 = Button(window,text="Acelerar1",command=acelerar1)
btnacelerar1.grid(column=1,row=0)

btndesacelerar1 = Button(window,text="Desacelerar1",command=desacelerar1)
btndesacelerar1.grid(column=0,row=0)

lblv2 = Label(window,text=str(velocidad2))
lblv2.grid(column=3,row=1)

lblcarro2 = Label(window,text=" "*150)
lblcarro2.grid(column=4,row=1)

hilo2 = None

def acelerar2():
    global hilo2
    if hilo2:
        global velocidad2
        if velocidad2<5:
            velocidad2 = velocidad2 + 1
            lblv2.configure(text=str(velocidad2))
    else:
        print("Hilo 2 creado")
        hilo2 = threading.Thread(target=recorriendo, args=(2,))
        # Inicia el Hilo
        hilo2.start()
        
def desacelerar2():
    global velocidad2
    if velocidad2 >0:
        velocidad2 = velocidad2 - 1
        lblv2.configure(text=str(velocidad2))
    
btnacelerar2 = Button(window,text="Acelerar2",command=acelerar2)
btnacelerar2.grid(column=1,row=1)

btndesacelerar2 = Button(window,text="Desacelerar2",command=desacelerar2)
btndesacelerar2.grid(column=0,row=1)

window.mainloop()
