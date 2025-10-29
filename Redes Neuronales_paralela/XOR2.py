import numpy as np
import threading
import math
import random

class Neurona:
    def __init__(self, tasa_aprendizaje=0.65):
        self.n = tasa_aprendizaje    # tasa de aprendizaje
        self.W = None                # pesos sinapticos
        self.U = None                # umbrales 
        self.itera = 0
        self.Emc = 1e10              # error medio cuadratico
        print("Neurona creada.")

    # funcion de activacion, su rango esta en [0,1] (funcion signoide)
    def f(self, x):
        return 1.0 / (1.0 + math.exp(-x))

    # derivada de la funcion de activacion
    def fprima(self, x):
        fx = self.f(x)
        return fx * (1.0 - fx)

    # entrenamiento (ejecutado en hilo)
    def operar(self, X, T, maxitera, minError):
        while self.itera < maxitera and self.Emc > minError:
            self.itera += 1
            errores = []

            for p in range(len(X)):
                # propagacion hacia adelante
                neta0 = X[p][0]*self.W[0] + X[p][1]*self.W[2] - self.U[0]
                neta1 = X[p][0]*self.W[1] + X[p][1]*self.W[3] - self.U[1]
                fneta0 = self.f(neta0)
                fneta1 = self.f(neta1)
                neta2 = fneta0*self.W[4] + fneta1*self.W[5] - self.U[2]
                fneta2 = self.f(neta2)# salida obtenida

                #retropropagacion
                landa2 = (T[p] - fneta2) * self.fprima(neta2)
                landa1 = self.fprima(neta1) * landa2 * self.W[5]
                landa0 = self.fprima(neta0) * landa2 * self.W[4]

                # actualizacion de pesos para el nodo salida
                self.W[4] += self.n * landa2 * fneta0
                self.W[5] += self.n * landa2 * fneta1

                # actualizacion de pesos de la capa oculta
                self.W[0] += self.n * landa0 * X[p][0]
                self.W[1] += self.n * landa1 * X[p][0]
                self.W[2] += self.n * landa0 * X[p][1]
                self.W[3] += self.n * landa1 * X[p][1]

                # actualizacion de umbrales
                self.U[2] += -self.n * landa2
                self.U[1] += -self.n * landa1
                self.U[0] += -self.n * landa0

                # error cuadratico medio parcial
                errores.append(0.5 * (T[p] - fneta2)**2)

            self.Emc = np.mean(errores)
            print(f"Iteración {self.itera} | Error medio cuadrático = {self.Emc:.6f}")
            
        print("\nPesos sinápticos aprendidos:")
        print("W =", np.round(self.W, 4))
        print("U =", np.round(self.U, 4))
        print("Iteraciones:", self.itera)
        print("Error final:", self.Emc)

    # inicializa pesos y lanza el hilo de entrenamiento
    def entrenar(self, X, T, maxitera, minError):
        self.W = [random.random() for _ in range(6)]
        self.U = [random.random() for _ in range(3)]
        hilo = threading.Thread(target=self.operar, args=(X, T, maxitera, minError))
        hilo.start()
        hilo.join()

    # evaluacion
    def mapear(self, Xi):
        neta0 = Xi[0]*self.W[0] + Xi[1]*self.W[2] - self.U[0]
        neta1 = Xi[0]*self.W[1] + Xi[1]*self.W[3] - self.U[1]
        fneta0 = self.f(neta0)
        fneta1 = self.f(neta1)
        neta2 = fneta0*self.W[4] + fneta1*self.W[5] - self.U[2]
        fneta2 = self.f(neta2)
        if fneta2>0.5:
            return 1
        else:
            return 0


# ====================== USO ==========================

# XOR con entradas (-1,1)
X = np.array([
    [1.0,  1.0],
    [1.0, 0.0],
    [0.0, 1.0],
    [0.0, 0.0]
])

T = np.array([0.0, 1.0, 1.0, 0.0])

maxitera = 10000
minError = 0.01

n = Neurona()
n.entrenar(X, T, maxitera, minError)

print("\n----- PRUEBA DE MAPEO -----")
for i in range(len(X)):
    print(f"{X[i]} → {n.mapear(X[i])}")
