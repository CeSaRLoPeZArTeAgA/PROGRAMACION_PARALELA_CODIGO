import numpy as np
import threading
import math
import random


# Clase Neurona individual (para capa oculta o salida)
class Neurona(threading.Thread):
    def __init__(self, entradas, tasa_aprendizaje=0.65):
        threading.Thread.__init__(self)
        self.n = tasa_aprendizaje
        self.W = [random.random() for _ in range(entradas)]
        self.U = random.random()
        self.salida = 0.0
        self.landa = 0.0
        self.neta = 0.0

    def f(self, x):
        return 1.0 / (1.0 + math.exp(-x))

    def fprima(self, x):
        fx = self.f(x)
        return fx * (1.0 - fx)

    def forward(self, X):
        self.neta = np.dot(self.W, X) - self.U
        self.salida = self.f(self.neta)
        return self.salida

    def actualizar(self, deltaW, deltaU):
        for i in range(len(self.W)):
            self.W[i] += deltaW[i]
        self.U += deltaU

# red neuronal XOR con backpropagation
class RedXOR:
    def __init__(self, tasa_aprendizaje=0.65):
        self.n = tasa_aprendizaje
        # 2 neuronas en la capa oculta, 1 en la de salida
        self.h1 = Neurona(2, tasa_aprendizaje)
        self.h2 = Neurona(2, tasa_aprendizaje)
        self.o1 = Neurona(2, tasa_aprendizaje)
        self.Emc = 1e10
        self.itera = 0

    def entrenar(self, X, T, maxitera, minError):
        while self.itera < maxitera and self.Emc > minError:
            errores = []
            for p in range(len(X)):
                x = X[p]
                t = T[p]

                # propagacion hacia adelante
                # cada neurona de la capa oculta se ejecuta en un hilo
                salidas_ocultas = [0, 0]

                def h1_forward():
                    salidas_ocultas[0] = self.h1.forward(x)

                def h2_forward():
                    salidas_ocultas[1] = self.h2.forward(x)

                hilo1 = threading.Thread(target=h1_forward)
                hilo2 = threading.Thread(target=h2_forward)
                hilo1.start()
                hilo2.start()
                hilo1.join()
                hilo2.join()

                salida_oculta = np.array(salidas_ocultas)
                salida_final = self.o1.forward(salida_oculta)

                # ======= Retropropagación =======
                landa2 = (t - salida_final) * self.o1.fprima(self.o1.neta)
                landa1 = self.h1.fprima(self.h1.neta) * landa2 * self.o1.W[0]
                landa0 = self.h2.fprima(self.h2.neta) * landa2 * self.o1.W[1]

                # ======= Actualización de pesos (en hilos) =======
                def actualizar_o1():
                    deltaW = [self.n * landa2 * salida_oculta[i] for i in range(2)]
                    deltaU = -self.n * landa2
                    self.o1.actualizar(deltaW, deltaU)

                def actualizar_h1():
                    deltaW = [self.n * landa1 * x[i] for i in range(2)]
                    deltaU = -self.n * landa1
                    self.h1.actualizar(deltaW, deltaU)

                def actualizar_h2():
                    deltaW = [self.n * landa0 * x[i] for i in range(2)]
                    deltaU = -self.n * landa0
                    self.h2.actualizar(deltaW, deltaU)

                h3 = threading.Thread(target=actualizar_o1)
                h4 = threading.Thread(target=actualizar_h1)
                h5 = threading.Thread(target=actualizar_h2)
                h3.start(); h4.start(); h5.start()
                h3.join(); h4.join(); h5.join()

                errores.append(0.5 * (t - salida_final)**2)

            self.Emc = np.mean(errores)
            self.itera += 1
            print(f"Iteración {self.itera} | Error medio cuadrático = {self.Emc:.6f}")

        print("\nPesos sinápticos aprendidos:")
        print("h1.W =", np.round(self.h1.W, 4), "U =", round(self.h1.U, 4))
        print("h2.W =", np.round(self.h2.W, 4), "U =", round(self.h2.U, 4))
        print("o1.W =", np.round(self.o1.W, 4), "U =", round(self.o1.U, 4))
        print("Iteraciones:", self.itera)
        print("Error final:", self.Emc)

    def mapear(self, Xi):
        salida_oculta = np.array([self.h1.forward(Xi), self.h2.forward(Xi)])
        salida_final = self.o1.forward(salida_oculta)
        return 1 if salida_final > 0.5 else 0


# USO - XOR con entradas en {0,1}
if __name__ == "__main__":
    X = np.array([
        [1.0, 1.0],
        [1.0, 0.0],
        [0.0, 1.0],
        [0.0, 0.0]
    ])

    T = np.array([0.0, 1.0, 1.0, 0.0])

    red = RedXOR()
    red.entrenar(X, T, maxitera=10000, minError=0.01)

    print("\n----- PRUEBA DE MAPEO -----")
    for i in range(len(X)):
        print(f"{X[i]} → {red.mapear(X[i])}")
