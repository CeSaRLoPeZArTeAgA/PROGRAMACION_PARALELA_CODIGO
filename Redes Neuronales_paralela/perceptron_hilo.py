import random
import numpy as np
import threading
class Neurona:
    e = 0.5
    w = np.array([random.random(),random.random()])
    u = random.random()
    def __init__(self):
        print("Creado")
    
    def operar(self,X,T):
        i = 0
        while (i<4):
            y = sum(X[i][:]*self.w[:]) - self.u
            Y = -1.0
            if y>=0.0:
                Y = 1.0
       
            if(Y!=T[i]):
                self.w[0] = self.w[0]+2.0*self.e*T[i]*X[i][0]
                self.w[1] = self.w[1]+2.0*self.e*T[i]*X[i][1]
                self.u = self.u+2*self.e*T[i]*(-1)
                i = -1
            i = i + 1
        print("Terminado entrenamiento")
        
    def entrenar(self,X,T):
        hilo = threading.Thread(target=self.operar, args=(X,T,))
        hilo.start()
        hilo.join()
    def mapear(self,Xi):
        y = Xi[0]*self.w[0]+ Xi[1]*self.w[1] - self.u
        if y >=0:
            return 1.0
        else:
            return -1.0

X = np.array([[1.0,1.0],
       [1.0,-1.0],
       [-1.0,1.0],
       [-1.0,-1.0]])

T = np.array([[1.0],[1.0],[1.0],[-1.0]])
n = Neurona()
n.entrenar(X,T)
print("----- mapeo ----------")
for i in range(4):
    print(X[i,:],n.mapear(X[i,:]))
