# ===========================================================
# ex6.py - Experimento SECUENCIAL vs PARALELO con OpenGL
#           + Gráfico de rendimiento
# ===========================================================
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import math
import random
import time
import multiprocessing as mp
import matplotlib.pyplot as plt

# -----------------------------------------------------------
# Clase punto 3D
# -----------------------------------------------------------
class Point3D:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x, self.y, self.z = x, y, z


# -----------------------------------------------------------
# Genera puntos sobre la superficie de una esfera
# -----------------------------------------------------------
def generar_puntos_esfera(num_points, radio=3.0):
    puntos = []
    for _ in range(num_points):
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)
        x = radio * math.sin(phi) * math.cos(theta)
        y = radio * math.sin(phi) * math.sin(theta)
        z = radio * math.cos(phi)
        puntos.append(Point3D(x, y, z))
    return puntos


# -----------------------------------------------------------
# Inicialización OpenGL
# -----------------------------------------------------------
def init_gl():
    glClearColor(0.05, 0.05, 0.05, 1.0)
    glEnable(GL_DEPTH_TEST)
    glPointSize(2.0)


# -----------------------------------------------------------
# Dibuja los puntos de una esfera
# -----------------------------------------------------------
def dibujar_puntos(puntos):
    glBegin(GL_POINTS)
    for p in puntos:
        glColor3f(abs(p.x) / 3, abs(p.y) / 3, abs(p.z) / 3)
        glVertex3f(p.x, p.y, p.z)
    glEnd()


# -----------------------------------------------------------
# Dibujo secuencial
# -----------------------------------------------------------
def dibujar_secuencial(puntos):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -8.0)
    dibujar_puntos(puntos)
    glutSwapBuffers()


# -----------------------------------------------------------
# Dibujo paralelo (usa multiprocessing)
# -----------------------------------------------------------
def procesar_punto(p):
    # Simula trabajo por hilo
    return (abs(p.x), abs(p.y), abs(p.z))


def dibujar_paralelo(puntos):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -8.0)

    with mp.Pool(processes=mp.cpu_count()) as pool:
        colores = pool.map(procesar_punto, puntos)

    glBegin(GL_POINTS)
    for p, c in zip(puntos, colores):
        glColor3f(c[0] / 3, c[1] / 3, c[2] / 3)
        glVertex3f(p.x, p.y, p.z)
    glEnd()
    glutSwapBuffers()


# -----------------------------------------------------------
# Mide tiempo de dibujo de una simulación OpenGL
# -----------------------------------------------------------
def medir_tiempo(num_points, modo):
    puntos = generar_puntos_esfera(num_points)
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(f"Modo {modo} | {num_points} puntos".encode("utf-8"))
    init_gl()

    start = time.time()
    if modo == "SECUENCIAL":
        dibujar_secuencial(puntos)
    else:
        dibujar_paralelo(puntos)
    end = time.time()

    glutDestroyWindow(glutGetWindow())
    return end - start


# -----------------------------------------------------------
# Experimento completo y gráfico
# -----------------------------------------------------------
def experimento_opengl():
    tamaños = [50000, 100000, 150000]
    repeticiones = 3

    print("\n================== EXPERIMENTO OPENGL AUTOMATIZADO ==================\n")
    resultados = []

    for num_points in tamaños:
        print(f">>> {num_points} puntos por esfera")
        tiempos_seq, tiempos_par = [], []

        for r in range(repeticiones):
            print(f"  Repetición {r + 1} SECUENCIAL...")
            t_seq = medir_tiempo(num_points, "SECUENCIAL")
            print(f"    Tiempo SEQ: {t_seq:.4f} s")
            tiempos_seq.append(t_seq)

            print(f"  Repetición {r + 1} PARALELO...")
            t_par = medir_tiempo(num_points, "PARALELO")
            print(f"    Tiempo HILOS: {t_par:.4f} s\n")
            tiempos_par.append(t_par)

        prom_seq = sum(tiempos_seq) / repeticiones
        prom_par = sum(tiempos_par) / repeticiones
        speedup = prom_seq / prom_par if prom_par > 0 else 0

        resultados.append((num_points, prom_seq, prom_par, speedup))

    # -------------------------------------------------------
    # Imprimir resultados promedio
    # -------------------------------------------------------
    print("\n====================== RESULTADOS PROMEDIO ======================")
    print(" Puntos\t\tSEQ(s)\t\tHILOS(s)\tSpeedup")
    print("---------------------------------------------------------------")
    for n, t1, t2, sp in resultados:
        print(f" {n:<10}\t{t1:.4f}\t\t{t2:.4f}\t\t{sp:.2f}x")
    print("===============================================================\n")

    # -------------------------------------------------------
    # Gráficos de tendencia
    # -------------------------------------------------------
    puntos = [r[0] for r in resultados]
    tiempos_seq = [r[1] for r in resultados]
    tiempos_par = [r[2] for r in resultados]
    speedups = [r[3] for r in resultados]

    plt.figure(figsize=(10, 6))
    plt.plot(puntos, tiempos_seq, 'o-', label="Secuencial", linewidth=2)
    plt.plot(puntos, tiempos_par, 's-', label="Hilos (Paralelo)", linewidth=2)
    plt.title("Tiempos promedio de ejecución vs número de puntos", fontsize=14)
    plt.xlabel("Número de puntos por esfera", fontsize=12)
    plt.ylabel("Tiempo promedio (s)", fontsize=12)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # -------------------------------------------------------
    # Gráfico de Speedup
    # -------------------------------------------------------
    plt.figure(figsize=(8, 5))
    plt.plot(puntos, speedups, 'd--', color='purple', linewidth=2)
    plt.title("Speedup paralelo vs tamaño del problema", fontsize=14)
    plt.xlabel("Número de puntos por esfera", fontsize=12)
    plt.ylabel("Speedup (Tseq / Tpar)", fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# -----------------------------------------------------------
# Main
# -----------------------------------------------------------
if __name__ == "__main__":
    experimento_opengl()
