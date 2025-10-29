import numpy as np
from PIL import Image
import threading
import time
import random
import matplotlib.pyplot as plt

# FUNCIONES AUXILIARES

#calcula el gradiente horizontal
def calcular_Gx(I, Mh, Gx):
    m, n = I.shape
    for i in range(1, m-1):
        for j in range(1, n-1):
            P = I[i-1:i+2, j-1:j+2]
            Gx[i, j] = (P * Mh).sum()

#calcula el gradiente vertical
def calcular_Gy(I, Mv, Gy):
    m, n = I.shape
    for i in range(1, m-1):
        for j in range(1, n-1):
            P = I[i-1:i+2, j-1:j+2]
            Gy[i, j] = (P * Mv).sum()

# resalta bordes usando funcion convencional - version secuencial
def resaltarborde(I, Mh, Mv):
    m, n = I.shape
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
    m, n = I.shape
    Gx = np.zeros((m, n))
    Gy = np.zeros((m, n))
    h1 = threading.Thread(target=calcular_Gx, args=(I, Mh, Gx))
    h2 = threading.Thread(target=calcular_Gy, args=(I, Mv, Gy))
    h1.start();
    h2.start()
    h1.join(); 
    h2.join()
    Q = np.sqrt(Gx**2 + Gy**2)
    return Q

# =========================================================================================

# PROGRAMA PRINCIPAL

# numero fijo de repeticiones por tamaño
num_repeticiones = 5
print(f"\nNúmero fijo de repeticiones: {num_repeticiones}\n")

# cargar imagen base en escala de grises
imgGray = Image.open("paisaje.jpg").convert("L")
ancho_base, alto_base = imgGray.size
print(f"Tamaño original: {ancho_base}x{alto_base}")

# filtros de Roberts
robertH = np.array([[0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                    [0.0, 0.0, -1.0]])

robertV = np.array([[0.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0],
                    [0.0, -1.0, 0.0]])

# listas globales para graficar
tamaños = []
promedios_funcion = []
promedios_hilos = []

# BUCLE DE ESCALADO
aux=5 # numero de escalamientos para el analisis
for escala in range(aux):
    factor = 2 ** escala
    nuevo_ancho = int(ancho_base * factor)
    nuevo_alto = int(alto_base * factor)
    tamaños.append(nuevo_ancho * nuevo_alto)

    print(f"\nIteración de tamaño {escala+1}/aux: {nuevo_ancho}x{nuevo_alto}")

    # redimensionar imagen
    img_resized = imgGray.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
    imgNP = np.array(img_resized)

    tiempos_funcion = []
    tiempos_hilos = []

    for k in range(num_repeticiones):
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

    # mostrar estadísticos de este tamaño
    print("   Promedios parciales:")
    print(f"   -> Función normal: {np.mean(tiempos_funcion):.4f} s")
    print(f"   -> Con hilos:      {np.mean(tiempos_hilos):.4f} s")

    # guardar resultados
    promedios_funcion.append(np.mean(tiempos_funcion))
    promedios_hilos.append(np.mean(tiempos_hilos))


# GRAFICAR RESULTADOS
plt.figure(figsize=(8,5))
plt.plot(tamaños, promedios_funcion, 'o-r', label="Función normal")
plt.plot(tamaños, promedios_hilos, 'o-b', label="Con hilos")
plt.title("Comparación de tiempos según tamaño de imagen")
plt.xlabel("Número de píxeles (ancho × alto)")
plt.ylabel("Tiempo promedio (segundos)")
plt.xscale("log")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

print("\n\n --- FIN DEL EXPERIMENTO 2 ---")
