import numpy as np
from PIL import Image
import threading  # librería para trabajar con hilos

n, m = 0, 0

def calcular_Gx(I, Mh, Gx):
    """Calcula el gradiente horizontal."""
    for i in range(1, m-1):
        for j in range(1, n-1):
            P = I[i-1:i+2, j-1:j+2]
            Gx[i, j] = (P * Mh).sum()

def calcular_Gy(I, Mv, Gy):
    """Calcula el gradiente vertical."""
    for i in range(1, m-1):
        for j in range(1, n-1):
            P = I[i-1:i+2, j-1:j+2]
            Gy[i, j] = (P * Mv).sum()

def resaltarborde_hilos(I, Mh, Mv):
    """Calcula el borde usando hilos para Gx y Gy."""
    Gx = np.zeros((m, n))
    Gy = np.zeros((m, n))

    # Crear los hilos
    hilo1 = threading.Thread(target=calcular_Gx, args=(I, Mh, Gx))
    hilo2 = threading.Thread(target=calcular_Gy, args=(I, Mv, Gy))

    # Iniciar los hilos
    hilo1.start()
    hilo2.start()

    # Esperar a que ambos terminen
    hilo1.join()
    hilo2.join()

    # Combinar resultados (magnitud del gradiente)
    Q = np.sqrt(Gx**2 + Gy**2)
    return Q

# -----------------------------------------------------
# PROGRAMA PRINCIPAL
# -----------------------------------------------------
imgGray = Image.open("paisaje.jpg").convert("L")
imgGray.show()

n, m = imgGray.size
imgNP = np.array(imgGray)

# Filtros de Roberts
robertH = np.array([[0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                    [0.0, 0.0, -1.0]])

robertV = np.array([[0.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0],
                    [0.0, -1.0, 0.0]])

# Aplicación del filtro con hilos
resultado = resaltarborde_hilos(imgNP, robertH, robertV)

# Mostrar resultado
im = Image.fromarray(resultado)
im.show()
