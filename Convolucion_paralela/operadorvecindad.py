import numpy as np
from PIL import Image #para abrir, convertir y mostrar imágenes.
n,m = 0,0 # n ancho y m alto de la imagen. Definimos inicialmente en 0, 0

def filtrar3x3(I,M):
    Q = np.zeros((m,n))
    for i in range(1,m-1):
        for j in range(1,n-1):
            P = I[i-1:i+2,j-1:j+2]
            Q[i,j] = (P*M).sum()        
    return Q

def filtrar5x5(I,M):
    Q = np.zeros((m,n))
    for i in range(2,m-2):
        for j in range(2,n-2):
            P = I[i-1:i+2,j-1:j+2]
            Q[i,j] = (P*M).sum()        
    return Q

def resaltarborde(I,Mh,Mv):
    Q = np.zeros((m,n))
    for i in range(1,m-1):
        for j in range(1,n-1):
            P = I[i-1:i+2,j-1:j+2]
            Gx = (P*Mh).sum()# operar con un hilo (Hilo 1)
            Gy = (P*Mv).sum()# operar con un hilo (Hilo 2)
            Q[i,j] = (Gx*Gx + Gy*Gy)**0.5       
    return Q

imgGray = Image.open("paisaje.jpg").convert("L")#carga la imagen y lo convierte a grises "L"
imgGray.show()# mostrar la imagen por pantalla

n,m = imgGray.size
imgNP = np.array(imgGray)#imagen de pillow a matrix np
#promedio = (1.0/9.0)*np.ones((3,3))
#gaussiano = np.ones((3,3))
#gaussiano = np.array([[1.0/16.0,2.0/16.0,1.0/16.0],
#                      [2.0/16.0,4.0/16.0,2.0/16.0],
#                      [1.0/16.0,2.0/16.0,1.0/16.0]])

#resultado = filtrar3x3(imgNP,promedio)

# para filtro de BORDES
prewittV = np.array([[1.0,0.0,-1.0],
                     [1.0,0.0,-1.0],
                     [1.0,0.0,-1.0]])
prewittH = np.array([[-1.0,-1.0,-1.0],
                     [0.0,0.0,0.0],
                     [1.0,1.0,1.0]])

# para filtro  de derivada
sobelH = np.array([[1.0,0.0,-1.0],
                   [2.0,0.0,-2.0],
                   [1.0,0.0,-1.0]])
sobelV = np.array([[-1.0,-2.0,-1.0],
                     [0.0,0.0,0.0],
                     [1.0,2.0,1.0]])

# filtrado para detectar diagonales
robertH = np.array([[0.0,0.0,0.0],
                   [0.0,1.0,0.0],
                   [0.0,0.0,-1.0]])

robertV = np.array([[0.0,0.0,0.0],
                    [0.0,0.0,1.0],
                    [0.0,-1.0,0.0]])

#aplicacion de filtro 
resultado = resaltarborde(imgNP,robertH,robertV)
im = Image.fromarray(resultado)#la matriz np pasarlo a imagen pillow
im.show()
