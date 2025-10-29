import numpy as np
import multiprocessing as mp
from threading import Thread
import time
tam = 500
A = np.random.randint(0, 10, size=(tam, tam))
B = np.random.randint(0, 10, size=(tam, tam))
#print("A:",A)
#print("B:",B)
m,n = A.shape
init = time.time()
resultado = np.matmul(A,B) # A @ B
print('Time 0 Numpy => ' + str(time.time() - init))
result = np.zeros((m, m))
init = time.time()
for i in range(len(A)):
   for j in range(len(A[0])):
       for k in range(len(A)):           
            result[i][j] += A[i][k] * B[k][j]            
print('Time 1 proceso => ' + str(time.time() - init))


global s
s = np.zeros((m, m))
def multiplicar(F,C,i,j):
    global s    
    s[i,j] = sum(F*C)    
    
hilos = {}
init = time.time()
for i in range(len(A)):
    fila = A[i,:]
    for j in range(len(A)):        
        #print("fila",fila)
        columna = B[:,j]
        #print("columna",columna)
        hilos[i] = Thread(target=multiplicar, args=(fila,columna,i,j,))
        hilos[i].start()        
print('Time 2 Hilos =>' + str(time.time() - init))
#print("s:",s)
    
