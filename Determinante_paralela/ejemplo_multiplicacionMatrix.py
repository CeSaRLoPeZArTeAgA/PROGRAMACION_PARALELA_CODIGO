import numpy as np
import time
import os
import threading


# Dimensiones
m, n, p = 40, 30, 50   # A será (40x30), B será (30x50), resultado será (40x50)

# Matriz A de tamaño (m x n)
A = np.random.randint(1, 10, size=(m, n))

# Matriz B de tamaño (n x p)
B = np.random.randint(1, 10, size=(n, p))


# función para calcular un elemento de la matriz C
def filacol(i, j, A, B, resultado):
    suma = 0
    for k in range(len(B)):  # recorrer columnas de A / filas de B
        suma += A[i][k] * B[k][j]
    resultado[i][j] = suma


if __name__ == "__main__":
    num_hilos = os.cpu_count()   

    # ----------------------------
    # Multiplicación con numpy
    # ----------------------------
    init = time.time()
    resultado_numpy = np.dot(A, B)  
    tFinal1 = time.time() - init

    # ----------------------------
    # Multiplicación manual
    # ----------------------------
    init = time.time()
    resultado_manual = [[0 for _ in range(len(B[0]))] for _ in range(len(A))]

    for i in range(len(A)):
        for j in range(len(B[0])):
            for k in range(len(B)):
                resultado_manual[i][j] += A[i][k] * B[k][j]

    tFinal2 = time.time() - init

    # ----------------------------
    # Multiplicación con hilos
    # ----------------------------
    init = time.time()
    resultado_hilos = [[0 for _ in range(len(B[0]))] for _ in range(len(A))]
    threads = []

    for i in range(len(A)):
        for j in range(len(B[0])):
            t = threading.Thread(target=filacol, args=(i, j, A, B, resultado_hilos))
            threads.append(t)
            t.start()

    # esperar que todos los hilos terminen
    for t in threads:
        t.join()

    tFinal3 = time.time() - init

    # ----------------------------
    # Resultados
    # ----------------------------
    print(f"\n--------  RESUMEN DE MULTIPLICACIÓN ---------")
    print(f"Número de hilos (CPU detectados): {num_hilos}")
    print(f"Tiempo total con numpy: {tFinal1:.10f} segundos")
    print(f"Tiempo total manual: {tFinal2:.10f} segundos")
    print(f"Tiempo total con hilos: {tFinal3:.10f} segundos")

    #print("\nResultado con numpy:")
    #print(resultado_numpy)

    #print("\nResultado manual:")
    #print(resultado_manual)

    #print("\nResultado con hilos:")
    #print(resultado_hilos)
