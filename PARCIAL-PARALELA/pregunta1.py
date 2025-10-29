import numpy as np
from PIL import Image
import threading
import time
import random
import matplotlib.pyplot as plt

# variables globales
n, m = 0, 0

#calcula el gradiente horizontal
def calcular_Gx(I, Mh, Gx):
    for i in range(1, m-1):
        for j in range(1, n-1):
            P = I[i-1:i+2, j-1:j+2]
            Gx[i, j] = (P * Mh).sum()

#calcula el gradiente vertical
def calcular_Gy(I, Mv, Gy):
    for i in range(1, m-1):
        for j in range(1, n-1):
            P = I[i-1:i+2, j-1:j+2]
            Gy[i, j] = (P * Mv).sum()

# resalta bordes usando funcion convencional
def resaltarborde(I, Mh, Mv):
    Q = np.zeros((m, n))
    for i in range(1, m-1):
        for j in range(1, n-1):
            P = I[i-1:i+2, j-1:j+2]
            Gx = (P * Mh).sum()
            Gy = (P * Mv).sum()
            Q[i, j] = np.sqrt(Gx**2 + Gy**2)
    return Q

# resalta bordes usando hilos (Gx y Gy en paralelo)
def resaltarborde_hilos(I, Mh, Mv):
    Gx = np.zeros((m, n))
    Gy = np.zeros((m, n))

    hilo1 = threading.Thread(target=calcular_Gx, args=(I, Mh, Gx))
    hilo2 = threading.Thread(target=calcular_Gy, args=(I, Mv, Gy))

    hilo1.start()
    hilo2.start()
    hilo1.join()
    hilo2.join()

    Q = np.sqrt(Gx**2 + Gy**2)
    return Q

######################################################################################

# PROGRAMA PRINCIPAL

#  escoger numero aleatorio de repeticiones(para poder poner el numero que se quiera)
num_repeticiones = random.randint(2, 10)
print(f"\nNumero aleatorio de repeticiones: {num_repeticiones}\n")

# cargar imagen en escala de grises
imgGray = Image.open("paisaje.jpg").convert("L")
n, m = imgGray.size
imgNP = np.array(imgGray)

# filtros de Roberts
robertH = np.array([[0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                    [0.0, 0.0, -1.0]])

robertV = np.array([[0.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0],
                    [0.0, -1.0, 0.0]])

# listas para almacenar tiempos
tiempos_funcion = []
tiempos_hilos = []

# repetir el experimento
for k in range(num_repeticiones):
    print(f"Iteración {k+1}/{num_repeticiones}")

    # metodo normal
    t0 = time.time()
    resultado_funcion = resaltarborde(imgNP, robertH, robertV)
    tf = time.time() - t0
    tiempos_funcion.append(tf)

    # metodo con hilos
    t0 = time.time()
    resultado_hilos = resaltarborde_hilos(imgNP, robertH, robertV)
    tf2 = time.time() - t0
    tiempos_hilos.append(tf2)

# mostrar resumen de resultados
print("\n--------  ESTADÍSTICAS DE EJECUCION USANDO FILTRO DE ROBERT ---------")
for i in range(num_repeticiones):
    print(f"Iteracion {i+1}: Funcion = {tiempos_funcion[i]:.4f}s | Hilos = {tiempos_hilos[i]:.4f}s")

print("\nPROMEDIOS:")
print(f"Tiempo medio (funcion): {np.mean(tiempos_funcion):.4f} s")
print(f"Tiempo medio (hilos): {np.mean(tiempos_hilos):.4f} s")
print("\n....Cierre la imagen para que muestres las imagenes que se desarrollaron por ambos metodos")

# generar grafica de comparacion
plt.figure(figsize=(8, 5))
plt.plot(range(1, num_repeticiones+1), tiempos_funcion, 'o-r', label="Función normal")
plt.plot(range(1, num_repeticiones+1), tiempos_hilos, 'o-b', label="Con hilos")
plt.title("Comparación de tiempos de ejecución")
plt.xlabel("Iteración")
plt.ylabel("Tiempo (segundos)")
plt.legend()
plt.grid(True)
plt.show()

# Normalizar resultados a 0-255 y convertir a uint8 antes de crear las imágenes
im1 = Image.fromarray((resultado_funcion / np.max(resultado_funcion) * 255).astype(np.uint8))
im2 = Image.fromarray((resultado_hilos / np.max(resultado_hilos) * 255).astype(np.uint8))

# guardar con nombres personalizados
im1.save("bordes_funcion.png")
im2.save("bordes_hilos.png")

# mostrar las imágenes guardadas
im1.show(title="Última imagen - Función normal")
im2.show(title="Última imagen - Con hilos")

print("\nImágenes guardadas como:")
print(" - bordes_funcion.png")
print(" - bordes_hilos.png")
print("\n\n--- FIN DEL EXPERIMENTO 1---")

