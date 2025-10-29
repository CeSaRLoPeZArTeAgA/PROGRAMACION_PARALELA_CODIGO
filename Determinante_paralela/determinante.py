import numpy as np
import sympy as sym 
sym.init_printing(use_unicode=True)
import copy 
import random 
import time
import os
import threading
import multiprocessing as mp



# Elimina la i-ésima fila y la j-ésima columna de A
def makeM(A,i,j): 
   
    M = copy.deepcopy(A) 
    del M[i] 
    for k in range(len(M)): 
        del M[k][j] 
    return M 

# Calcular el determinante de la matriz de lista de listas A
def mydet(A): 
    if type(A) == np.matrix: 
        A = A.tolist()    
    n = len(A) 
    if n == 2: 
        det = (A[0][0]*A[1][1] - A[1][0]*A[0][1])  
        return det 
    det = 0 
    i = 0 
    for j in range(n): 
        M = makeM(A,i,j) 
        
        #Calculo del determinate 
        det += (A[i][j] * ((-1)**(i+j+2)) * mydet(M)) 
    return det

# calculo con hilos y menores complementarios
def mydet_threaded(A):
    if type(A) == np.matrix:
        A = A.tolist()
    n = len(A)
    if n == 2:
        return A[0][0]*A[1][1] - A[1][0]*A[0][1]

    results = [0] * n
    threads = []

    def worker(j):
        M = makeM(A, 0, j)
        results[j] = A[0][j] * ((-1)**j) * mydet(M)

    # Crear hilos
    for j in range(n):
        t = threading.Thread(target=worker, args=(j,))
        threads.append(t)
        t.start()

    # Esperar hilos
    for t in threads:
        t.join()

    return sum(results)


#calculo con eliminacion gausisana y multiprocesadores

# aplica eliminación gaussiana sobre una fila i usando el pivote k
def eliminar_fila(args): 
    A, i, k = args
    if A[k, k] == 0:
        return A[i, :]
    factor = A[i, k] / A[k, k]
    A[i, k:] = A[i, k:] - factor * A[k, k:]
    return A[i, :]

#calculo del determinante por eliminación gaussiana paralelizada
def det_gauss_parallel(A):
    
    A = A.astype(float).copy()
    n = A.shape[0]
    signo = 1

    for k in range(n-1):
        # pivoteo parcial
        max_row = np.argmax(abs(A[k:, k])) + k
        if A[max_row, k] == 0:
            return 0
        if max_row != k:
            A[[k, max_row]] = A[[max_row, k]]
            signo *= -1

        # preparar argumentos para las filas i = k+1..n
        filas = [(A.copy(), i, k) for i in range(k+1, n)]

        # paralelizar la actualización de filas
        with mp.Pool(processes=mp.cpu_count()) as pool:
            nuevas_filas = pool.map(eliminar_fila, filas)

        # reemplazar filas actualizadas
        for idx, i in enumerate(range(k+1, n)):
            A[i, :] = nuevas_filas[idx]

    return signo * np.prod(np.diag(A))

# main principal
if __name__ == "__main__":
    #numero de hilo del cpu
    num_hilos = os.cpu_count()   

    #generate aleatoria de la matrix que se calculara el determinante 
    n = 10  #dimension de la matrix (nxn)
    s = 10  #valor maximo de las entradas de la matrix
    A = [[round(random.random()*s) for i in range(n)] for j in range(n)] 
    A = np.matrix(A) 

    #calculo de determinante usando numpy
    init = time.time()
    detA_py = np.linalg.det(A)
    tFinal1 = time.time() - init
    
    #calculo de determinante usando menores complementarios (recursivo)
    init = time.time()
    detA_rec= mydet(A)
    tFinal2 = time.time() - init
    
    #calculo de determinante usando hilos metodo de menores complementarios
    init = time.time()
    detA_threaded_1 = mydet_threaded(A)
    tFinal3 = time.time() - init 
    
    #calculo de determinante usando hilos metodo de eliminacion gaussiana
    init = time.time()
    detA_threaded_2 = det_gauss_parallel(A)
    tFinal4 = time.time() - init 
    
    
    # IMPRESION DE RESULTADOS
    print(f"\n--------  RESUMEN DE CALCULO DE DETERMINANTE DE UNA MATRIZ  ---------\n")

    print(f"Matrix A(nxn) generada:\n")
    print(A)

    print(f"\nNúmero de hilos (CPU detectados): {num_hilos}\n")

    print(f"Determinante de A(numpy): {detA_py}")
    print(f"Tiempo total con numpy: {tFinal1:.10f} segundos\n")

    print(f"Determinante de A(recursiva): {detA_rec}")
    print(f"Tiempo total manual: {tFinal2:.10f} segundos\n")

    print(f"Determinante de A(hilo_1): {detA_threaded_1}")
    print(f"Tiempo total con hilos: {tFinal3:.10f} segundos\n")

    print(f"Determinante de A(hilo_2): {detA_threaded_2}")
    print(f"Tiempo total con hilos: {tFinal4:.10f} segundos\n")


