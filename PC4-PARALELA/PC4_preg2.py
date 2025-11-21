import numpy as np
import math
import os
from PIL import Image
import threading
import os
import time
import matplotlib.pyplot as plt   

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
     [0,0,0.125,0,0]], np.float32)


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
def kohonen_salidas(E,W): # E: representativo,W: pesos
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
    patron = imarray[1:m-1, 1:n-1]    # 254x254
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

#############  MULTIPLES CORRIDAS AUTOMATICAS ##############
# guardar tiempos:
epocas = []
tiempos_secuencial = []
tiempos_paralelo = []

# cargar patrones una sola vez
EEE = np.zeros([15,324],np.float32)
nombres = [
    'arco1.tif','whorl1.tif','right1.tif','left1.tif',
    'arco2.tif','whorl2.tif','right2.tif','left2.tif',
    'arco3.tif','whorl3.tif','right3.tif','left3.tif',
    'arco4.tif','whorl4.tif','right4.tif'
]
for k in range(15):
    EEE[k,:] = representativo(nombres[k])

# bucle externo: 500 → 1000
for max_iter in range(500, 1001, 100):

    print("\n===================================================")
    print(f"EJECUTANDO ENTRENAMIENTO DE MODELOS (epoch = {max_iter})")
    
    # reiniciar matrices para cada corrida
    W = np.zeros([324,14,14])
    for i in range(324):
        W[i,2:12,2:12] = np.random.rand(10,10)

    M_t = np.zeros([14,14],np.float32)
    M_index = np.zeros([10,10],np.float32)

    # MODELO SECUENCIAL
    t1 = time.perf_counter()
    for iter in range(max_iter):
        for i in range(15):
            E = EEE[i,:]
            M = kohonen_salidas(E,W)
            M_t,W,x,y = kohonen_reforzamiento(M,M_t,0.45,EEE[0,:],W)
    t2 = time.perf_counter()
    tiempo_seq = t2 - t1

    # MODELO PARALELO
    t3 = time.perf_counter()
    for iter in range(max_iter):
        for i in range(15):
            E = EEE[i,:]
            M = kohonen_salidas_hilos(E,W)
            M_t,W,x,y = kohonen_reforzamiento(M,M_t,0.45,EEE[0,:],W)
    t4 = time.perf_counter()
    tiempo_par = t4 - t3
    # impresion de resultado, linea a linea
    print(f"Tiempo Secuencial:{tiempo_seq:.2f} seg, Tiempo Paralisado:{tiempo_par:.2f} seg")

    # guardar resultados para la grafica
    epocas.append(max_iter)
    tiempos_secuencial.append(tiempo_seq)
    tiempos_paralelo.append(tiempo_par)


#  graficando Epoch VS Tiempo (para ambos modelos)
plt.figure(figsize=(10,6))
plt.plot(epocas, tiempos_secuencial, marker='o', label="Mod. Secuencial")
plt.plot(epocas, tiempos_paralelo, marker='o', label="Mod. Paralelo (Hilos)")
plt.xlabel("Epoch (iteracion)")
plt.ylabel("Tiempo de entrenamiento (segundos)")
plt.title("Grafico Estadistico Epoch vs Tiempo ")
plt.grid(True)
plt.legend()
plt.savefig("grafico_epoch_vs_tiempo.png", dpi=300, bbox_inches='tight')
plt.show()
