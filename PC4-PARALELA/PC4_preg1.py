import numpy as np
import math
import os
from PIL import Image
import threading
import os
import time

 # numero de hilos a crear sera igual al numero procesadores disponibles
num_threads = os.cpu_count() 

'''
Se implementa una red de Kohonen (SOM) para clasificar huellas
digitales en 4 tipos:

LEFT_LOOP
RIGHT_LOOP
WHORL
ARCO
'''
# datos globales
LEFT_LOOP   = 1
RIGHT_LOOP  = 2
WHORL       = 3
ARCO        = 4

#matriz de 5×5 da el peso de vecindad de cada neurona alrededor 
#de la ganadora. El centro (1) es máxima influencia, y los demás 
# decaen tipo gaussiano discreto
vecindad_gaussiana = np.array(
    [[0,0,0.125,0,0],
     [0,0.25,0.5,0.25,0],
     [0.125,0.5,1,0.5,0.125],
     [0,0.25,0.5,0.25,0],
     [0,0,0.125,0,0]]
    ,np.float32)

# crear una matriz de pesos sinapticos
# 324: dimensión del vector de entrada (orientaciones).
# 14×14: mapa 2D de neuronas extendido (el núcleo útil es 10×10 desde [2:12, 2:12]).
# se inicializa en cero y luego se llena la zona válida 2:12 con pesos aleatorios entre 0 y 1.
W = np.zeros([324,14,14])
for i in range(324):
    W[i,2:12,2:12] = np.random.rand(10,10)
    
# Crear una matriz temporal
# M_t[x,y] guarda cuántas veces ha ganado la neurona (x,y)
# sirve para que la tasa de aprendizaje alpha decrezca localmente
M_t = np.zeros([14,14],np.float32)

# crear la matriz de indices o resultante de lo aprendido
M_index = np.zeros([10,10],np.float32)
max_iter = 500# maximo cantidad de generaciones (epoch)
alpha_max = 0.45#factor de aprendizaje inicial

# definen los kernels Sobel gx, gy.
def sobel(patron):
    m,n = patron.shape
    I = np.array(patron,np.float32)
    Gx = np.zeros([m-2,n-2],np.float32)
    Gy = np.zeros([m-2,n-2],np.float32)
    gx = [[-1,0,1],[-2,0,2],[-1,0,1]]
    gy = [[1,2,1],[0,0,0],[-1,-2,-1]]
    for i in range(1,m-2):
        for j in range(1,n-2):
            Gx[i-1,j-1] = sum(sum(I[i-1:i+2,j-1:j+2]*gx))
            Gy[i-1,j-1] = sum(sum(I[i-1:i+2,j-1:j+2]*gy))
    return Gx,Gy

# filtro de mediana 3×3. Hace un padding de 1 píxel (para d=3) alrededor de G
def medfilt2(G,d=3):
    m,n = G.shape
    temp = np.zeros([m+2*(d//2),n+2*(d//2)],np.float32)
    salida = np.zeros([m,n],np.float32)
    temp[1:m+1,1:n+1] = G
    for i in range(1,m):
        for j in range(1,n):
            A = np.asarray(temp[i-1:i+2,j-1:j+2]).reshape(-1)
            salida[i-1,j-1] = np.sort(A)[d+1]
    return salida

# mapa de orientaciones
def orientacion(patron,w):
    Gx,Gy = sobel(patron)
    Gx = medfilt2(np.array(Gx,np.float32))
    Gy = medfilt2(np.array(Gy,np.float32))
    m,n = Gx.shape
    mOrientaciones = np.zeros([m//w,n//w],np.float32)
    for i in range(m//w):
        for j in range(n//w):
            YY = sum(sum(2*Gx[i*w:(i+1)*w,0:1]*Gy[i*w:(i+1)*w,0:1]))
            XX = sum(sum(Gx[i*w:(i+1)*w,0:1]**2-Gy[i*w:(i+1)*w,0:1]**2))
            mOrientaciones[i,j] = (0.5*math.atan2(YY,XX) + math.pi/2.0)*(18.0/math.pi)
    return mOrientaciones


# calculo de salidas de la red SOM, usando programacion secuencial
def kohonen_salidas(E,W):# E: representativo,W: pesos
    M = np.zeros([14,14],np.float32)
    m = 14
    for x in range(2,m-2):
        for y in range(2,m-2):
            w = W[:,x,y]
            num = sum(E*w)
            denom = math.sqrt(sum(E**2)*sum(w**2))
            if num==0 or denom==0:
                M[x,y] = 0.0
            else:
                M[x,y] = num/denom
    return M

# calculo de salidas de la red SOM, usando hilos                       
def kohonen_salidas_hilos(E, W):
    global num_threads
    """
    Calcula la matriz M de similitudes coseno usando hilos (threading).
    """
    # subrutina interna (por hilo)
    def _kohonen_chunk_thread(E, W, M, x_start, x_end, E_norm):
        """
        calcula la similitud coseno para filas x_start:x_end
        y escribe resultados directamente en M
        """
        for x in range(x_start, x_end):
            for y in range(2, 12):
                w = W[:, x, y]
                w_norm = math.sqrt((w*w).sum())

                denom = E_norm * w_norm
                if denom != 0:
                    M[x, y] = (E*w).sum() / denom
                else:
                    M[x, y] = 0.0

    # comienza la función paralela
    M = np.zeros((14,14), np.float32)

    # normamos E una sola vez
    E_norm = math.sqrt((E*E).sum())

    # rango util de x = 2 .. 11 (10 filas)
    total_filas = 10
    filas_por_hilo = total_filas // num_threads

    threads = []
    x_inicio = 2

    for i in range(num_threads):
        x_fin = x_inicio + filas_por_hilo
        if i == num_threads - 1:
            x_fin = 12  # incluir ultima fila valida

        t = threading.Thread(
            target=_kohonen_chunk_thread,
            args=(E, W, M, x_inicio, x_fin, E_norm)
        )
        threads.append(t)
        t.start()

        x_inicio = x_fin

    # esperamos a que todos los hilos terminen
    for t in threads:
        t.join()

    return M

# regla de aprendizaje
def kohonen_reforzamiento(M1,M_t,alpha_max,E,W):
    (yy,xx) = np.unravel_index(np.argmax(M1,axis=None),M1.shape)
    t = M_t[xx+2,yy+2] + 1
    M_t[xx+2,yy+2] = t
    alpha = alpha_max/t
    i = 0
    for x in range(xx-1,xx+3):
        j = 0
        for y in range(yy-1,yy-3):
            w = W[:,x,y]
            vg = vecindad_gaussiana[i,j]
            d = E.T - w
            W[:,x,y] = w + alpha*d*vg# actualizando los pesos sinapticos
            j = j + 1
        i = i + 1
    return M_t,W,xx-2,yy-2
        
# vector representativo de una imagen
def representativo(archivo):
    # Listar todos los archivos del directorio actual
    archivos = os.listdir(os.getcwd())

    # Buscar archivo ignorando mayusculas/minusculas
    archivo_encontrado = None
    for f in archivos:
        if f.lower() == archivo.lower():
            archivo_encontrado = f
            break

    # Si no se encuentra, mostrar error con información clara
    if archivo_encontrado is None:
        raise FileNotFoundError(f"No se encontró '{archivo}'")

    # Abrir ahora el archivo verdadero encontrado
    im = Image.open(archivo_encontrado)
    m, n = im.size
    imarray = np.array(im, np.float32)
    patron = imarray[1:m-1, 1:n-1]   # 254x254
    EE = orientacion(patron, 14)      # 18x18
    return np.asarray(EE).reshape(-1) # 1x324

# clasificacion de una imagen
def mapear(archivo,W,M_index):
    E = representativo(archivo)
    M = kohonen_salidas(E,W)
    (yy,xx) = np.unravel_index(np.argmax(M,axis=None),M.shape)
    x = xx - 2
    y = yy - 2
    tipo = M_index[x,y]
    print(x,y,tipo)
    if tipo==LEFT_LOOP:
        print("LEFT_LOOP")
    if tipo==RIGHT_LOOP:
        print("RIGHT_LOOP")
    if tipo==WHORL:
        print("WHORL")
    if tipo==ARCO:
        print("ARCO")
        

# bloque principal: creacion de patrones y entrenamiento
print("---------------------------------------------------------")
print("creando los patrones de entrada")
EEE = np.zeros([15,324],np.float32)
EEE[0,:] = representativo('arco1.tif')
EEE[1,:] = representativo('whorl1.tif')
EEE[2,:] = representativo('right1.tif')
EEE[3,:] = representativo('left1.tif')
EEE[4,:] = representativo('arco2.tif')
EEE[5,:] = representativo('whorl2.tif')
EEE[6,:] = representativo('right2.tif')
EEE[7,:] = representativo('left2.tif')
EEE[8,:] = representativo('arco3.tif')
EEE[9,:] = representativo('whorl3.tif')
EEE[10,:] = representativo('right3.tif')
EEE[11,:] = representativo('left3.tif')
EEE[12,:] = representativo('arco4.tif')
EEE[13,:] = representativo('whorl4.tif')
EEE[14,:] = representativo('right4.tif')
# inicia el proceso de entrenamiento de la RN, programacion secuencial
print("---------------------------------------------------------")
tiempo_inicio1 = time.perf_counter()# inicio de toma de lectura de tiempo
print("iniciando el aprendizaje")
for iter in range(max_iter):
    print(iter)
    for i in range(15):
        E = EEE[i,:]
        M = kohonen_salidas(E,W)
        M_t,W,x,y = kohonen_reforzamiento(M,M_t,alpha_max,EEE[0,:],W)
        if i in [0,4,8,12]:
            M_index[x,y] = ARCO
        elif i in [3,7,11]:
            M_index[x,y] = LEFT_LOOP
        elif i in [2,6,10,14]:
            M_index[x,y] = RIGHT_LOOP
        elif i in [1,5,9,13]:
            M_index[x,y] = WHORL
print("Fin del aprendizaje")
tiempo_fin1 = time.perf_counter()# fin de toma de lectura de tiempo
tiempo_total1 = tiempo_fin1 - tiempo_inicio1 #tiempo total de entrenamiento de modelo



# Inicia el proceso de entrenamiento de la RN usando hilos
print("---------------------------------------------------------")
tiempo_inicio2 = time.perf_counter()# inicio de toma de lectura de tiempo
print("iniciando el aprendizaje")
for iter in range(max_iter):
    print(iter)
    for i in range(15):
        E = EEE[i,:]
        M = kohonen_salidas_hilos(E,W)
        M_t,W,x,y = kohonen_reforzamiento(M,M_t,alpha_max,EEE[0,:],W)
        if i in [0,4,8,12]:
            M_index[x,y] = ARCO
        elif i in [3,7,11]:
            M_index[x,y] = LEFT_LOOP
        elif i in [2,6,10,14]:
            M_index[x,y] = RIGHT_LOOP
        elif i in [1,5,9,13]:
            M_index[x,y] = WHORL
print("Fin del aprendizaje")
tiempo_fin2 = time.perf_counter()# fin de toma de lectura de tiempo
tiempo_total2 = tiempo_fin2 - tiempo_inicio2 #tiempo total de entrenamiento de modelo

print("---------------------------------------------------------")
print("Matriz de indices o representacion de lo aprendido: ")
print(M_index)
print("")
print("---------------------------------------------------------")
print("###  RESUMEN DE CALCULOS - COMPROBACION DE MODELO   ###")
print("")
print("Numero hilos para la paralizacion(CPU):",num_threads)
print(f"Tiempo total de entrenamiento para modelo usando progra. secuencial: {tiempo_total1:.4f} segundos")
print(f"Tiempo total de entrenamiento para modelo usando Paralelismo(hilos): {tiempo_total2:.4f} segundos")
print(f"Numero de iteraciones para ambos modelos (epoch): {max_iter:.4f} segundos")

print("")
print("-> pasamos a corroborar el modelo, con los archivos que tengamos....")
while True:
    print("")
    print("...para salir del programa ingrese x + enter.... ")
    mifile = input("Ingrese el nombre del file (sin .tif): ")

    # si el usuario escribe x → finalizar
    if mifile.lower() == "x":
        print("")
        print("....Cerrando la aplicacion.....")
        print("")
        break

    try:
        mapear(mifile + '.tif', W, M_index)
    except Exception as e:
        print("Error:", e)