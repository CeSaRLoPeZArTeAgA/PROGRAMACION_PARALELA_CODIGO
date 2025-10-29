import time
import threading
import random
import math
import matplotlib.pyplot as plt

# ===========================================================
# Clases base simplificadas (solo para cálculo de tiempos)
# ===========================================================
class Point3D:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

class Surface3D:
    def __init__(self):
        self.points = []

    def sphere_points(self, num_points=1000, radius=1.0):
        self.points = []
        for _ in range(num_points):
            theta = random.uniform(0, 2 * math.pi)
            phi = math.acos(2 * random.uniform(0, 1) - 1)
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            self.points.append(Point3D(x, y, z))

class Esfera:
    def __init__(self, num_points, radio):
        self.surface = Surface3D()
        self.surface.sphere_points(num_points=num_points, radius=radio)
        self.angulo = math.radians(random.randint(20, 80))
        self.velocidad_inicial = random.randint(20, 40)
        self.velocidad_x = self.velocidad_inicial * math.cos(self.angulo)
        self.velocidad_y = self.velocidad_inicial * math.sin(self.angulo)
        self.gravedad = -9.8
        self.tiempo = 0.0
        self.dt = 0.05
        self.altura = 0.0

    def actualizar(self):
        self.tiempo = 0.0
        self.altura = 0.0
        while True:
            self.tiempo += self.dt
            self.altura = self.velocidad_y * self.tiempo + 0.5 * self.gravedad * self.tiempo ** 2
            if self.altura <= 0:
                break
            # Simula el tiempo de cómputo por puntos
            _ = [p.x * p.y for p in self.surface.points[:100]]
            time.sleep(0.00001)

# ===========================================================
# Funciones de simulación
# ===========================================================
def simulacion_secuencial(num_points):
    esferas = [Esfera(num_points, 3) for _ in range(2)]
    inicio = time.time()
    for e in esferas:
        e.actualizar()
    fin = time.time()
    return fin - inicio

def simulacion_hilos(num_points):
    esferas = [Esfera(num_points, 3) for _ in range(2)]
    inicio = time.time()

    threads = []
    for e in esferas:
        t = threading.Thread(target=e.actualizar)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    fin = time.time()
    return fin - inicio

# ===========================================================
# Ejecución experimental con promedios
# ===========================================================
num_points_list = [50000, 100000, 150000]
repeticiones = 3

tiempos_seq = []
tiempos_thr = []

for n in num_points_list:
    print(f"\n=== Probando con {n} puntos ===")
    tiempos_s = [simulacion_secuencial(n) for _ in range(repeticiones)]
    tiempos_t = [simulacion_hilos(n) for _ in range(repeticiones)]

    prom_s = sum(tiempos_s) / repeticiones
    prom_t = sum(tiempos_t) / repeticiones

    print(f"Promedio Secuencial: {prom_s:.3f} s")
    print(f"Promedio con Hilos : {prom_t:.3f} s")

    tiempos_seq.append(prom_s)
    tiempos_thr.append(prom_t)

# ===========================================================
# Gráfico comparativo tipo el de la pregunta
# ===========================================================
plt.figure(figsize=(8, 6))
x = range(len(num_points_list))
width = 0.35

plt.bar([i - width/2 for i in x], tiempos_seq, width, color='orange', label='sH (Secuencial)')
plt.bar([i + width/2 for i in x], tiempos_thr, width, color='green', label='cH (Con Hilos)')

plt.xticks(x, [str(n) for n in num_points_list])
plt.xlabel("Cantidad de puntos por esfera")
plt.ylabel("Tiempo promedio de ejecución (s)")
plt.title("Comparación de tiempo de ejecución\nMovimiento parabólico sin hilos y con hilos")
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.6)

plt.show()
