import numpy as np
import threading
import math
import random
import os

# implementacion de la clase neurona simple
class Neurona(threading.Thread):
    def __init__(self, entradas, tasa_aprendizaje=0.65):
        threading.Thread.__init__(self)
        self.n = tasa_aprendizaje
        self.W = [random.random() for _ in range(entradas)]
        self.U = random.random()
        self.salida = 0.0
        self.landa = 0.0
        self.neta = 0.0

    #funcion de activacion, el cual solo entrega valores en el rango [0,1]
    #por eso la data de entrenamiento tiene que estar entre [0,1]
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

#red neuronal XOR(con numero variable de neuronas ocultas)
class RedXOR:
    def __init__(self, n_ocultas=2, tasa_aprendizaje=0.65):
        self.n = tasa_aprendizaje
        self.n_ocultas = n_ocultas
        # crear capa oculta
        self.capa_oculta = [Neurona(2, tasa_aprendizaje) for _ in range(n_ocultas)]
        # neurona de salida
        self.o1 = Neurona(n_ocultas, tasa_aprendizaje)
        self.Emc = 1e10
        self.itera = 0

    def entrenar(self, X, T, maxitera, minError):
        while self.itera < maxitera and self.Emc > minError:
            errores = []
            for p in range(len(X)):
                x = X[p]
                t = T[p]

                # propagacion hacia adelante 
                salidas_ocultas = [0] * self.n_ocultas
                hilos = []

                for i, h in enumerate(self.capa_oculta):
                    hilo = threading.Thread(target=lambda i=i, h=h: salidas_ocultas.__setitem__(i, h.forward(x)))
                    hilos.append(hilo)
                    hilo.start()
                for hilo in hilos:
                    hilo.join()

                salida_oculta = np.array(salidas_ocultas)
                salida_final = self.o1.forward(salida_oculta)

                # retropropagacion
                landa_salida = (t - salida_final) * self.o1.fprima(self.o1.neta)

                landas_ocultas = [
                    h.fprima(h.neta) * landa_salida * self.o1.W[i]
                    for i, h in enumerate(self.capa_oculta)
                ]

                # actualizacion de pesos (Hacemos cada actualización en un hilo)
                hilos = []

                def actualizar_salida():
                    deltaW = [self.n * landa_salida * salida_oculta[i] for i in range(self.n_ocultas)]
                    deltaU = -self.n * landa_salida
                    self.o1.actualizar(deltaW, deltaU)

                hilos.append(threading.Thread(target=actualizar_salida))

                for i, h in enumerate(self.capa_oculta):
                    def actualizar_oculta(h=h, landa=landas_ocultas[i]):
                        deltaW = [self.n * landa * x[j] for j in range(2)]
                        deltaU = -self.n * landa
                        h.actualizar(deltaW, deltaU)
                    hilos.append(threading.Thread(target=actualizar_oculta))

                for hilo in hilos:
                    hilo.start()
                for hilo in hilos:
                    hilo.join()

                errores.append(0.5 * (t - salida_final) ** 2)

            self.Emc = np.mean(errores)
            self.itera += 1
            print(f"Iteración {self.itera} | Error medio cuadrático = {self.Emc:.6f}")

        print("\nPesos sinápticos aprendidos:")
        for i, h in enumerate(self.capa_oculta):
            print(f"h{i+1}.W = {np.round(h.W, 4)}  U = {round(h.U, 4)}")
        print("o1.W =", np.round(self.o1.W, 4), "U =", round(self.o1.U, 4))
        print("Iteraciones:", self.itera)
        print("Error final:", self.Emc)

    def mapear(self, Xi):
        salida_oculta = np.array([h.forward(Xi) for h in self.capa_oculta])
        salida_final = self.o1.forward(salida_oculta)
        return 1 if salida_final > 0.5 else 0


# entrenamiento de la red neuronal
if __name__ == "__main__":
    
    #ojo: la data de entrenamiento es 0 y 1
    X = np.array([
        [1.0, 1.0],
        [1.0, 0.0],
        [0.0, 1.0],
        [0.0, 0.0]
    ])

    T = np.array([0.0, 1.0, 1.0, 0.0])
    
    print("\n############### ENTRENAMIENTO DE LA RED NEURONAL(AUTOMATICO) - XOR #################\n")
    # numero de hilos a crear sera igual al numero procesadores disponibles
    n_ocultas = os.cpu_count()   
    print("Numero de procesadores:",n_ocultas)
    print("Numero de neuronas en la capa oculta:",n_ocultas)
     # pausa para que el usuario lea
    input("\nPresione ENTER para continuar con el entrenamiento...\n")
    
    red = RedXOR(n_ocultas=n_ocultas)
    red.entrenar(X, T, maxitera=10000, minError=0.01)

    print("\n----- PRUEBA DE MODELO ENTRENADO - XOR -----")
    print("Numero de procesadores:",n_ocultas)
    for i in range(len(X)):
        print(f"{X[i]} → {red.mapear(X[i])}")