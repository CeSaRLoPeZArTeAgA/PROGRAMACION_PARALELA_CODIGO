#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Examen Final – Computación Gráfica
Tema: Recorrido animado de deformación y subdivisión de puntos de control (P0 → P0')

Objetivos cubiertos:
  1. Visualizar el recorrido (animación) del movimiento de un vértice de control P0 hasta P0'.
  2. Permitir subdivisiones dinámicas del segmento P0–P0' (uniformes y jerárquicas usando el punto medio m).

Modelo:
  - Objeto base: cuadrilátero simple (4 vértices).
  - Un vértice (v2) es el vértice de control inicial (P0). Se “desplaza” siguiendo una trayectoria discreta de puntos
    interpolados hasta P0'.
  - Los demás vértices se deforman según un peso radial w = exp(-ALPHA * dist) respecto de P0 inicial (influencia local).
  - La trayectoria se puede refinar:
      * Subdivisión uniforme: aumenta el número de puntos intermedios lineales.
      * Subdivisión jerárquica (tecla 'b'): inserta puntos medios en P0→m y m→P0' (una capa por pulsación).
  - El usuario puede recolocar P0' con click izquierdo.

Controles:
  Espacio : Pausa/Reanuda animación.
  Enter   : Avanza un paso manual (solo si está pausado).
  n       : (Alternativo) Avanza un paso manual (pausa también).
  r       : Reset total (P0', subdivisiones, ALPHA).
  + / -   : Aumentar / Disminuir subdivisiones uniformes.
  1..9    : Fijar número exacto de subdivisiones uniformes.
  b       : Subdivisión jerárquica (inserta puntos medios entre P0–m y m–P0').
  m       : Recalcular punto medio m (por si se movió P0').
  a       : Activar/desactivar modo loop (al final vuelve a inicio).
  1 / 2   : Disminuir / Aumentar ALPHA (localidad de la deformación).
  Click IZQ: Cambiar P0' a la posición del click (NDC).
  q / ESC : Salir.

Dependencias:
  - Python 3.x
  - PyOpenGL  (pip install PyOpenGL PyOpenGL_accelerate)
  - freeglut3 (Ubuntu: sudo apt install freeglut3-dev)
"""

import sys
import math
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# ============================= PARÁMETROS GLOBALES =============================

WINDOW_W, WINDOW_H = 900, 700               # Tamaño de ventana
FRAME_DELAY_MS = 80                         # Intervalo (ms) entre “ticks” de animación
ALPHA = 6.0                                 # Factor de influencia radial (mayor => más local)
animating = True                            # True = animación corriendo
loop_mode = False                           # True = reinicia al terminar
subdivisions_uniform = 10                   # # inicial de subdivisiones uniformes
current_index = 0                           # Índice actual en la trayectoria
last_time = time.time()                     # (placeholder si quisieras usar tiempo real)

# Puntos clave
P0_INITIAL = [-0.2,  0.2]                   # Posición inicial P0
P0_TARGET  = [ 0.6, -0.4]                   # Destino inicial P0' (modificable con click)
point_m = None                              # Punto medio m (P0 ↔ P0')

# Trayectoria discreta (lista de puntos 2D)
control_points = []                         # Se llena con build_uniform_points()

# Objeto base: cuadrilátero (v2 es el vértice de control)
base_vertices = [
    [-0.4, -0.2],   # v0
    [-0.4,  0.2],   # v1
    [-0.2,  0.2],   # v2 (P0)
    [-0.2, -0.2],   # v3
]

# Vértices deformados (se recalculan en cada paso)
deformed_vertices = [v[:] for v in base_vertices]


# ============================= UTILIDADES DE TRAYECTORIA =============================

def lerp(a, b, t):
    """Interpolación lineal entre puntos 2D a y b (t en [0,1])."""
    return [a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t]


def build_uniform_points(n):
    """Genera n subdivisiones => n+1 puntos desde P0_INITIAL hasta P0_TARGET."""
    global control_points
    n = max(1, n)
    control_points = [lerp(P0_INITIAL, P0_TARGET, i / float(n)) for i in range(n + 1)]


def recompute_m():
    """Recalcula el punto medio m = (P0 + P0') / 2."""
    global point_m
    if not control_points:
        return
    point_m = lerp(control_points[0], control_points[-1], 0.5)


def hierarchical_subdivide():
    """
    Subdivisión jerárquica: crea
        P0, midpoint(P0,m), m, midpoint(m,P0'), P0'
    Una capa de refinamiento por pulsación. m se recalcula si no existe.
    """
    global control_points, point_m
    if len(control_points) < 2:
        return
    if point_m is None:
        recompute_m()

    P0 = control_points[0]
    P1 = control_points[-1]
    m = point_m
    mid_left = lerp(P0, m, 0.5)
    mid_right = lerp(m, P1, 0.5)
    control_points = [P0, mid_left, m, mid_right, P1]


def advance_index():
    """Avanza el índice de animación; respeta loop_mode."""
    global current_index
    current_index += 1
    if current_index >= len(control_points):
        if loop_mode:
            current_index = 0
        else:
            current_index = len(control_points) - 1


# ============================= DEFORMACIÓN DEL OBJETO =============================

def apply_deformation():
    """
    Calcula deformed_vertices dada la posición actual de P0 en la trayectoria.
    Modelo:
      - dx, dy = (P0_actual - P0_base)
      - Cada vértice v_i se desplaza: v'_i = v_i + w_i*(dx, dy)
      - w_i = exp(-ALPHA * dist_i) donde dist_i = distancia(v_i, P0_base).
    """
    global deformed_vertices
    if not control_points:
        return

    base_control = base_vertices[2]  # v2 = P0 base
    p_current = control_points[current_index]
    dx = p_current[0] - base_control[0]
    dy = p_current[1] - base_control[1]

    new_list = []
    for v in base_vertices:
        dist = math.dist(v, base_control)
        w = math.exp(-ALPHA * dist)
        new_list.append([v[0] + dx * w, v[1] + dy * w])
    deformed_vertices = new_list


# ============================= RENDER / DIBUJADO =============================

def draw_text(x, y, text):
    """Dibuja texto bitmap en coordenadas del mundo (Ortho)."""
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(ch))


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # --- Ejes ---
    glColor3f(0.55, 0.55, 0.55)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    glVertex2f(-1, 0); glVertex2f(1, 0)   # Eje X
    glVertex2f(0, -1); glVertex2f(0, 1)   # Eje Y
    glEnd()

    # --- Trayectoria ---
    if control_points:
        glColor3f(0.15, 0.70, 0.25)
        glLineWidth(2.0)
        glBegin(GL_LINE_STRIP)
        for p in control_points:
            glVertex2f(p[0], p[1])
        glEnd()

    # --- Puntos de control P0, intermedios, P0' ---
    if control_points:
        glPointSize(7.0)
        glBegin(GL_POINTS)
        # P0 (rojo)
        glColor3f(1.0, 0.25, 0.25)
        glVertex2f(control_points[0][0], control_points[0][1])
        # Intermedios (amarillo)
        glColor3f(1.0, 0.9, 0.2)
        for p in control_points[1:-1]:
            glVertex2f(p[0], p[1])
        # P0' (azul)
        glColor3f(0.2, 0.2, 1.0)
        glVertex2f(control_points[-1][0], control_points[-1][1])
        glEnd()

    # --- Punto m (magenta) ---
    if point_m is not None:
        glPointSize(9.0)
        glColor3f(0.88, 0.0, 0.88)
        glBegin(GL_POINTS)
        glVertex2f(point_m[0], point_m[1])
        glEnd()

    # --- Polígono deformado (relleno) ---
    glColor3f(0.92, 0.40, 0.15)
    glBegin(GL_POLYGON)
    for v in deformed_vertices:
        glVertex2f(v[0], v[1])
    glEnd()

    # --- Contorno (wireframe) ---
    glColor3f(0.0, 0.0, 0.0)
    glLineWidth(1.0)
    glBegin(GL_LINE_LOOP)
    for v in deformed_vertices:
        glVertex2f(v[0], v[1])
    glEnd()

    # --- HUD ---
    glColor3f(1, 1, 1)
    total_segments = max(0, len(control_points) - 1)
    draw_text(-0.98, 0.93, f"Segs={total_segments} Idx={current_index}/{len(control_points)-1 if control_points else 0}")
    draw_text(-0.98, 0.87, f"ALPHA={ALPHA:.2f} Loop={'ON' if loop_mode else 'OFF'} Anim={'ON' if animating else 'PAUSE'}")
    draw_text(-0.98, 0.81, "[ESP]Play [Enter/n]Paso [+/-]/1..9 subdiv [b]jerarq [m]re-m [1][2]infl [a]loop [click]P0' [q/Esc]Salir")

    glutSwapBuffers()


# ============================= TIMER / ANIMACIÓN =============================

def timer(value):
    """Callback periódico: avanza la animación si corresponde y vuelve a programar el timer."""
    if animating and control_points:
        advance_index()
        apply_deformation()
        glutPostRedisplay()
    glutTimerFunc(FRAME_DELAY_MS, timer, 0)


# ============================= ENTRADA (TECLADO / MOUSE) =============================

def keyboard(key, x, y):
    """
    Manejo de teclado. GLUT entrega 'key' como bytes -> se decodifica a str.
    Enter se captura como '\r' (carriage return) o a veces '\n', así los tratamos juntos.
    """
    global animating, current_index, subdivisions_uniform, ALPHA, loop_mode

    k = key.decode('utf-8') if isinstance(key, bytes) else key

    if k == ' ':                           # Pausa / Reanuda
        animating = not animating

    elif k in ('\r', '\n'):                # Enter: paso manual si pausado
        if not animating and control_points:
            advance_index()
            apply_deformation()

    elif k == 'n':                         # Paso manual alternativo (pone en pausa)
        animating = False
        if control_points:
            advance_index()
            apply_deformation()

    elif k == 'r':                         # Reset completo
        reset_scene(full=True)

    elif k == '+':                         # Más subdivisiones uniformes
        subdivisions_uniform += 1
        rebuild_uniform_and_reset()

    elif k == '-':                         # Menos subdivisiones uniformes
        if subdivisions_uniform > 1:
            subdivisions_uniform -= 1
            rebuild_uniform_and_reset()

    elif k in '123456789':                 # Fijar subdivisiones exactas
        subdivisions_uniform = int(k)
        rebuild_uniform_and_reset()

    elif k == 'b':                         # Subdivisión jerárquica
        hierarchical_subdivide()
        current_index = 0
        apply_deformation()

    elif k == 'm':                         # Recalcular punto medio m
        recompute_m()
        glutPostRedisplay()

    elif k == '1':                         # Disminuir ALPHA (mínimo 0.5)
        ALPHA = max(0.5, ALPHA - 0.5)
        apply_deformation()

    elif k == '2':                         # Aumentar ALPHA
        ALPHA += 0.5
        apply_deformation()

    elif k == 'a':                         # Loop ON/OFF
        loop_mode = not loop_mode

    elif k in ('q', '\x1b'):               # Salir (q o ESC)
        try:
            glutLeaveMainLoop()
        except Exception:
            sys.exit(0)

    glutPostRedisplay()


def mouse(button, state, x, y):
    """Click izquierdo: recoloca P0_TARGET y reconstruye la trayectoria uniforme."""
    global P0_TARGET
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Convertir coords ventana -> NDC [-1,1]
        ndc_x = (x / float(WINDOW_W)) * 2.0 - 1.0
        ndc_y = -((y / float(WINDOW_H)) * 2.0 - 1.0)
        P0_TARGET = [ndc_x, ndc_y]
        rebuild_uniform_and_reset()
        glutPostRedisplay()


# ============================= REINICIOS / RECONSTRUCCIONES =============================

def rebuild_uniform_and_reset():
    """Reconstruye trayectoria uniforme con subdivisions_uniform y reinicia la animación."""
    global current_index
    build_uniform_points(subdivisions_uniform)
    recompute_m()
    current_index = 0
    apply_deformation()


def reset_scene(full=True):
    """Reset general. Si full=True, restablece P0_TARGET, subdivisiones y ALPHA."""
    global P0_TARGET, subdivisions_uniform, ALPHA, current_index
    if full:
        P0_TARGET[0], P0_TARGET[1] = 0.6, -0.4
        subdivisions_uniform = 10
        ALPHA = 6.0
    build_uniform_points(subdivisions_uniform)
    recompute_m()
    current_index = 0
    apply_deformation()


# ============================= INICIALIZACIÓN OPENGL/GLUT =============================

def init_gl():
    """Configura proyección ortográfica 2D y color de fondo."""
    glClearColor(0.12, 0.12, 0.14, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-1, 1, -1, 1)


def main():
    # Trayectoria inicial
    build_uniform_points(subdivisions_uniform)
    recompute_m()
    apply_deformation()

    # GLUT / Ventana
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutCreateWindow(b"Examen CG - Deformacion y Subdivision (Version Final)")

    # Callbacks
    init_gl()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)
    glutTimerFunc(FRAME_DELAY_MS, timer, 0)

    # Bucle principal
    glutMainLoop()


if __name__ == "__main__":
    main()
