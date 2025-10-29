import numpy as np

# --- Datos de entrenamiento (entradas y salidas) ---
X = np.array([
    [1, 1, 1, 1],
    [1, 0, 0, 1],
    [0, 1, 1, 1],
    [0, 0, 0, 1]
], dtype=float)

T = np.array([
    [1, 0],
    [0, 1],
    [1, 0],
    [0, 1]
], dtype=float)

# --- Parámetros ---
np.random.seed(42)
eta = 0.5      # tasa de aprendizaje
epochs = 10000

# Inicialización de pesos
W = np.random.uniform(-1, 1, (4, 3))   # pesos entrada -> capa oculta
U = np.random.uniform(-1, 1, (3, 2))   # pesos capa oculta -> salida
b1 = np.random.uniform(-1, 1, (1, 3))  # sesgos capa oculta
b2 = np.random.uniform(-1, 1, (1, 2))  # sesgos salida

# Función de activación (sigmoide)
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# Derivada de la sigmoide
def dsigmoid(x):
    return x * (1 - x)

# --- Entrenamiento ---
for epoch in range(epochs):
    # Propagación hacia adelante
    z_in = np.dot(X, W) + b1
    z = sigmoid(z_in)

    y_in = np.dot(z, U) + b2
    y = sigmoid(y_in)

    # Error
    error = T - y
    mse = np.mean(error**2)

    # Retropropagación
    delta2 = error * dsigmoid(y)
    delta1 = np.dot(delta2, U.T) * dsigmoid(z)

    # Actualización de pesos y sesgos
    U += eta * np.dot(z.T, delta2)
    b2 += eta * np.sum(delta2, axis=0, keepdims=True)
    W += eta * np.dot(X.T, delta1)
    b1 += eta * np.sum(delta1, axis=0, keepdims=True)

    # Mostrar cada 1000 iteraciones
    if epoch % 1000 == 0:
        print(f"Iteración {epoch} | Error cuadrático medio = {mse:.6f}")

# --- Resultados finales ---
print("\nPesos entrada -> oculta:\n", W)
print("\nPesos oculta -> salida:\n", U)

# Prueba
salida_final = sigmoid(np.dot(sigmoid(np.dot(X, W) + b1), U) + b2)
print("\nSalidas esperadas:\n", T)
print("\nSalidas obtenidas:\n", np.round(salida_final, 3))
