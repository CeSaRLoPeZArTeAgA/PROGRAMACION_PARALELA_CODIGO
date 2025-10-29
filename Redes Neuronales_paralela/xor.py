import numpy as np
import threading

# funcion de activacion
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# derivada de la 
def d_sigmoid(x):
    return x * (1 - x)

# clase de neurona ejecutada en un hilo
class Neurona(threading.Thread):
    def __init__(self, nombre, entradas, pesos, salida_dict, lock):
        super().__init__()
        self.nombre = nombre
        self.entradas = entradas
        self.pesos = pesos
        self.salida_dict = salida_dict
        self.lock = lock

    def run(self):
        salida = sigmoid(np.dot(self.entradas, self.pesos[:-1]) + self.pesos[-1])
        with self.lock:
            self.salida_dict[self.nombre] = float(salida)

#entrenamiento del XOR
if __name__ == "__main__":
    np.random.seed(42)

    # Entradas y salidas del XOR
    X = np.array([[0,0],[0,1],[1,0],[1,1]])
    y = np.array([[0],[1],[1],[0]])

    lr = 0.5
    epochs = 8000

    # pesos iniciales (2 entradas + bias)
    W1 = np.random.uniform(-1,1,(2,3))  # capa oculta
    W2 = np.random.uniform(-1,1,(1,3))  # capa de salida

    lock = threading.Lock()

    for epoch in range(epochs):
        total_error = 0.0

        for i in range(len(X)):
            entrada = X[i]
            objetivo = y[i]

            salidas = {}

            # crear hilos para neuronas ocultas
            hilos = []
            for j in range(2):
                h = Neurona(f"h{j}", entrada, W1[j], salidas, lock)
                hilos.append(h)
                h.start()

            # esperar que terminen
            for h in hilos:
                h.join()

            # obtener salida oculta
            salida_oculta = np.array([salidas["h0"], salidas["h1"]])

            # neurona de salida (en hilo)
            out_thread = Neurona("out", salida_oculta, W2[0], salidas, lock)
            out_thread.start()
            out_thread.join()

            salida_final = float(salidas["out"])
            error = float(objetivo - salida_final)
            total_error += abs(error)

            # retropropagacion
            d_out = error * d_sigmoid(salida_final)
            d_h = d_sigmoid(salida_oculta) * (d_out * W2[0, :-1])

            # actualizacion de pesos salida
            W2[0, :-1] += lr * d_out * salida_oculta
            W2[0, -1] += lr * d_out

            # actualizacion de pesos ocultos
            for j in range(2):
                W1[j, :-1] += lr * d_h[j] * entrada
                W1[j, -1] += lr * d_h[j]

        if epoch % 500 == 0:
            print(f"Iteración {epoch}: Error medio = {total_error/4:.5f}")

    # prueba final
    print("\n===== PRUEBA XOR =====")
    for entrada in X:
        salida_oculta = sigmoid(np.dot(W1[:,:-1], entrada) + W1[:,-1])
        salida_final = sigmoid(np.dot(W2[:,:-1], salida_oculta) + W2[:,-1])
        print(f"{entrada} → {salida_final[0]:.4f} → {int(salida_final[0]>0.5)}")




