import random
import numpy as np
import threading
import math
class Neurona:
    n = 0.65
    W = None#np.array([random.random(),random.random()])
    U = None#random.random()
    itera = -1
    Emc = 10000000
    def __init__(self):
        print("Creado")
        
    def f(self,x):
        return 1.0/(1.0+math.exp(-x))
    def fprima(self,x):
        return self.f(x)*(1.0-self.f(x))
        
    def operar(self,X,T,maxitera,minError):
        while self.itera<maxitera and self.Emc >minError:
            self.itera = self.itera + 1
            Error = [0.0,0.0,0.0,0.0]
            for p in range(4):
                neta0 = X[p][0]*self.W[0] + X[p][1]*self.W[2] - self.U[0]
                neta1 = X[p][0]*self.W[1] + X[p][1]*self.W[3] - self.U[1]
                fneta0 = self.f(neta0)
                fneta1 = self.f(neta1)
                neta2 = fneta0*self.W[4] + fneta1*self.W[5] - self.U[2]
                fneta2 = self.f(neta2)# salida obtenida
                landa2 = (T[p] - fneta2)*self.fprima(neta2)
                landa1 = self.fprima(neta1)*landa2*self.W[5]
                landa0 = self.fprima(neta0)*landa2*self.W[4]
                # actualizar los pesos sinapticos
                # los pesos de la capa salida
                self.W[5] = self.W[5] +self.n*landa2*fneta1
                self.W[4] = self.W[4] +self.n*landa2*fneta0
                # actualiza los pesos de la capa oculta
                self.W[0] = self.W[0] + self.n*landa0*X[p][0]
                self.W[1] = self.W[1] + self.n*landa1*X[p][0]
                self.W[2] = self.W[2] + self.n*landa0*X[p][1]
                self.W[3] = self.W[3] + self.n*landa1*X[p][1]
                # actualizar los umbrales
                self.U[2] = self.U[2] + self.n*landa2*-1
                self.U[1] = self.U[1] + self.n*landa1*-1
                self.U[0] = self.U[0] + self.n*landa0*-1
                Error[p] = 0.5*(T[p] - fneta2)*(T[p] - fneta2)
        
            self.Emc = (Error[0] + Error[1] + Error[2] + Error[3])/len(Error)
            print(self.itera," Error medio cuadratico: ",self.Emc)
        
        print("Pesos sinapticos aprendidos")
        
    def entrenar(self,X,T,maxitera,minError):
        self.W = [random.random() for _ in range(6)]
        self.U = [random.random() for _ in range(3)]
        hilo = threading.Thread(target=self.operar, args=(X,T,maxitera,minError,))
        hilo.start()
        hilo.join()
    
    def valor(x):
        if x>0.5:
            return 1
        else:
            return -1

    def mapear(self,Xi):
        neta0 = Xi[0]*self.W[0] + Xi[1]*self.W[2] - self.U[0]
        neta1 = Xi[0]*self.W[1] + Xi[1]*self.W[3] - self.U[1]
        fneta0 = self.f(neta0)
        fneta1 = self.f(neta1)
        neta2 = fneta0*self.W[4] + fneta1*self.W[5] - self.U[2]
        fneta2 = self.f(neta2)# salida obtenida
        if fneta2>0.5:
            return 1
        else:
            return -1

X = np.array([[1.0 , 1.0],
     [1.0, -1.0 ],
     [-1.0 , 1.0],
     [-1.0 ,-1.0]])
T = np.array([-1.0,1.0 ,1.0,-1.0])
n = Neurona()
maxitera = 10000
minError = 0.1
n.entrenar(X,T,maxitera,minError)
print("----- mapeo ----------")
for i in range(4):
    print(X[i,:],n.mapear(X[i,:]))
