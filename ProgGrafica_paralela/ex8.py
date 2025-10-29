from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import math
import random
import multiprocessing
import time
import threading

# ===========================================================
# Clases para las esferas y puntos 3D
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
            # elegir phi correctamente para distribución uniforme en esfera
            u = random.uniform(-1, 1)
            phi = math.acos(u)  # u = cos(phi)
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            self.points.append(Point3D(x, y, z))

class Esfera:
    def __init__(self, color, angulo_deg, velocidad_inicial, posx=0.0, points_count=2000):
        self.surface = Surface3D()
        self.surface.sphere_points(num_points=points_count, radius=3)
        self.color = color
        self.angulo = math.radians(angulo_deg)
        self.velocidad_inicial = velocidad_inicial
        self.posicion = [posx, 0.0, 0.0]  # x,y,z
        self.velocidad_x = velocidad_inicial * math.cos(self.angulo)
        self.velocidad_y = velocidad_inicial * math.sin(self.angulo)
        self.gravedad = -9.8
        self.tiempo = 0.0
        self.dt = 0.02
        self.activa = True
        self.lock = threading.Lock() 

    def actualizar(self):
        # actualizar estado fisico (llamado por hilo o por el main loop)
        if not self.activa:
            return
        self.tiempo += self.dt
        x_new = self.posicion[0] + self.velocidad_x * self.dt  # integracion simple por pasos
        y_new = self.velocidad_y * self.tiempo + 0.5 * self.gravedad * self.tiempo**2
        
        # calculamos x acumulando para mantener separacion inicial
        with self.lock:
            self.posicion[0] = x_new
            self.posicion[1] = y_new
            if self.posicion[1] <= 0:
                self.posicion[1] = 0
                self.activa = False

    def dibujar(self):
        with self.lock:
            px, py, pz = self.posicion
        glPushMatrix()
        glTranslatef(px, py, pz)
        glColor3f(self.color[0], self.color[1], self.color[2])
        glBegin(GL_POINTS)
        for p in self.surface.points:
            glVertex3f(p.x, p.y, p.z)
        glEnd()
        glPopMatrix()

# ===========================================================
# variables globales 
esferas = []
camera_pos = [0.0, 50.0, 100.0]
camera_target = [50.0, 25.0, 0.0]

# variables para controlar el tiempo de las esferas
tiempos_inicio = {}
tiempos_final = {}

# variable globales para guardar tiempos
tiempos_vuelo_secuencial = {}
tiempos_vuelo_hilos = {}

# para controlar las pasadas
initial_params = []
threaded_pass_started = False
thread_pool = []
mode = "SECUENCIAL"

# ===========================================================
# inicializacion de esferas
def inicializar_esferas(num_esferas=None):
    global esferas, initial_params, threaded_pass_started, mode, tiempos_inicio, tiempos_final, tiempos_vuelo_secuencial, tiempos_vuelo_hilos
    
    if num_esferas is None:
        num_esferas = multiprocessing.cpu_count()
    
    esferas = []
    
    initial_params = []
    tiempos_inicio = {}
    tiempos_final = {}
    tiempos_vuelo_secuencial = {}
    tiempos_vuelo_hilos = {}
    threaded_pass_started = False
    mode = "SECUENCIAL"

    # spacing en X para que no se monten
    spacing = 30.0
    total_width = spacing * (num_esferas - 1)
    start_x = - total_width / 2.0

    # reducir puntos por esfera según cantidad para mantener performance
    base_points = 50000
    points_per_sphere = max(1000, int(base_points / max(1, num_esferas)))

    # paleta simple
    paleta = []
    for i in range(num_esferas):
        paleta.append((random.random(), random.random(), random.random()))

    for i in range(num_esferas):
        ang = random.randint(20, 80)
        vel = random.randint(20, 40)
        posx = start_x + i * spacing
        e = Esfera(color=paleta[i], angulo_deg=ang, velocidad_inicial=vel, posx=posx, points_count=points_per_sphere)
        esferas.append(e)
        initial_params.append((ang, vel, posx))
        # registrar tiempos de inicio (se actualizarán al iniciar cada pasada)
        tiempos_inicio[i] = None
        tiempos_final[i] = None

# ------------------ Dibujo, suelo, ejes, info ------------------
def draw_ground():
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(-500, 0, -500)
    glVertex3f(500, 0, -500)
    glVertex3f(500, 0, 500)
    glVertex3f(-500, 0, 500)
    glEnd()
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_LINES)
    for x in range(-500, 501, 50):
        glVertex3f(x, 0.001, -500)
        glVertex3f(x, 0.001, 500)
    for z in range(-500, 501, 50):
        glVertex3f(-500, 0.001, z)
        glVertex3f(500, 0.001, z)
    glEnd()

def draw_axes(length=100.0):
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-length, 0.15, 0.0)
    glVertex3f(length, 0.15, 0.0)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0, -length*0.1, 0.0)
    glVertex3f(0, length*0.8, 0.0)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.15, -length)
    glVertex3f(0.0, 0.15, length)
    glEnd()

def display_info():
    glColor3f(1.0, 1.0, 1.0)
    info = []
    info.append("MOVIMIENTO DE ESFERAS - SECUENCIAL -> HILOS")
    info.append("")
    info.append(f"Numero esferas: {len(esferas)}  | Modo: {mode}")
    info.append("")
    for i, e in enumerate(esferas):
        ang_deg = math.degrees(e.angulo)
        estado = "ACTIVA" if e.activa else "REPOSO"
        info.append(f"Esfera {i+1}: Ang={ang_deg:.1f}°, Vel={e.velocidad_inicial:.1f} m/s - {estado}")
    info.append("")
    info.append("Controles: X,Y,Z mover camara | R reiniciar")
    for i, text in enumerate(info):
        glWindowPos2f(10, 580 - (i * 20))
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))
    # mostrar tiempos por esfera
    base_y = 580 - ((len(info)+1) * 20)
    for i in range(len(esferas)):
        if tiempos_inicio.get(i) is not None:
            if tiempos_final.get(i) is None:
                dur = time.time() - tiempos_inicio[i]
                txt = f"Esfera {i+1}: {dur:.2f} s (en vuelo)"
            else:
                dur = tiempos_final[i] - tiempos_inicio[i]
                estado = "finalizada"
                txt = f"Esfera {i+1}: {dur:.2f} s ({estado})"
            glWindowPos2f(10, base_y - i*20)
            for ch in txt:
                glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))

# ------------------ Display principal ------------------
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
              camera_target[0], camera_target[1], camera_target[2],
              0, 1, 0)
    draw_ground()
    draw_axes(200)
    for e in esferas:
        e.dibujar()
    display_info()
    glutSwapBuffers()

# ------------------ Simulación por hilos (visible) ------------------
def run_threaded_simulation_visible(params_list):
    global esferas, threaded_pass_started, mode, tiempos_inicio, tiempos_final, thread_pool, tiempos_vuelo_hilos
    # reset esferas con params_list (ang, vel, posx)
    esferas = []
    thread_pool = []
    mode = "HILOS"
    threaded_pass_started = True
    num = len(params_list)
    base_points = 50000
    points_per_sphere = max(1000, int(base_points / max(1, num)))
    for i, (ang, vel, posx) in enumerate(params_list):
        color = (random.random(), random.random(), random.random())
        e = Esfera(color=color, angulo_deg=ang, velocidad_inicial=vel, posx=posx, points_count=points_per_sphere)
        esferas.append(e)
        tiempos_inicio[i] = time.time()
        tiempos_final[i] = None
    # worker por esfera
    def worker(esfera_obj, idx):
        while esfera_obj.activa:
            esfera_obj.actualizar()
            time.sleep(esfera_obj.dt)
        tiempos_final[idx] = time.time()
        dur = tiempos_final[idx] - tiempos_inicio[idx]
        tiempos_vuelo_hilos[idx] = dur
        print(f"[HILOS] Esfera {idx+1} tiempo vuelo = {dur:.3f} s")

    for i, e in enumerate(esferas):
        t = threading.Thread(target=worker, args=(e, i), daemon=True)
        thread_pool.append(t)
        t.start()

    # refrescar pantalla mientras hay esferas activas
    def refrescar(_=0):
        glutPostRedisplay()
        activo = any(e.activa for e in esferas)
        if activo:
            glutTimerFunc(16, refrescar, 0)
        else:
            # cuando terminan todas, mostrar speedup respecto a la pasada secuencial si existe
            print("\n--- Todas las esferas en HILOS finalizaron ---")
            if tiempos_vuelo_secuencial:
                print("\n=== RESULTADOS DE ACELERACION (secuencial / hilos) ===")
                for i in sorted(tiempos_vuelo_secuencial.keys()):
                    t_seq = tiempos_vuelo_secuencial[i]
                    t_thr = tiempos_vuelo_hilos.get(i, t_seq)
                    speedup = t_seq / t_thr if t_thr > 0 else float('inf')
                    print(f"Esfera {i+1}: Sec={t_seq:.3f} s  Hilos={t_thr:.3f} s  Acel.={speedup:.2f}x")
    glutTimerFunc(16, refrescar, 0)

# ------------------ Update (modo SECUENCIAL) ------------------
def update(value):
    global tiempos_inicio, tiempos_final, threaded_pass_started, initial_params, mode, tiempos_vuelo_secuencial
    alguna_activa = False
    # si aún no iniciamos la secuencia, marcar tiempos_inicio
    for i, e in enumerate(esferas):
        if tiempos_inicio.get(i) is None:
            tiempos_inicio[i] = time.time()

    # actualizar cada esfera (secuencial, en el hilo principal)
    for i, e in enumerate(esferas):
        if e.activa:
            e.actualizar()
            alguna_activa = True
        else:
            if tiempos_final.get(i) is None:
                tiempos_final[i] = time.time()
                dur = tiempos_final[i] - tiempos_inicio[i]
                tiempos_vuelo_secuencial[i] = dur
                print(f"[SECUENCIAL] Esfera {i+1} finalizó en {dur:.3f} s")

    glutPostRedisplay()

    # si todas terminaron y no se lanzó la pasada con hilos, lanzarla
    if (not alguna_activa) and (not threaded_pass_started) and (mode == "SECUENCIAL"):
        # reconstruir params con posx desde initial_params
        params_copy = list(initial_params)
        # ajustar tiempos_inicio a None para la siguiente pasada
        for k in range(len(params_copy)):
            tiempos_inicio[k] = None
            tiempos_final[k] = None
        # Lanzar pasada por hilos
        run_threaded_simulation_visible(params_copy)

    glutTimerFunc(16, update, 0)

# ------------------ Reshape, teclado, especiales ------------------
def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / h if h != 0 else 1, 1, 2000)
    glMatrixMode(GL_MODELVIEW)

def keyboard(key, x, y):
    global camera_pos, camera_target, threaded_pass_started, mode
    try:
        key = key.decode("utf-8").lower()
    except:
        key = key.lower()
    if key == 'x':
        camera_pos[0] += 5; camera_target[0] += 5
    elif key == 'y':
        camera_pos[1] += 5; camera_target[1] += 5
    elif key == 'z':
        camera_pos[2] += 5; camera_target[2] += 5
    elif key == 'r':
        num = multiprocessing.cpu_count()
        inicializar_esferas(num_esferas=num)
        print("\n=== REINICIO SIMULACION ===")
        print(f"Num procesadores: {multiprocessing.cpu_count()}")
        for i, e in enumerate(esferas):
            print(f"Esfera {i+1}: Ang={math.degrees(e.angulo):.1f}°, Vel={e.velocidad_inicial} m/s, X0={e.posicion[0]:.1f}")
        threaded_pass_started = False
        mode = "SECUENCIAL"
    elif key == 'a':
        camera_pos[2] -= 5
    elif key == 's':
        camera_pos[2] += 5
    glutPostRedisplay()

def special_keys(key, x, y):
    global camera_pos
    if key == GLUT_KEY_LEFT:
        camera_pos[0] -= 5
    elif key == GLUT_KEY_RIGHT:
        camera_pos[0] += 5
    elif key == GLUT_KEY_UP:
        camera_pos[1] += 5
    elif key == GLUT_KEY_DOWN:
        camera_pos[1] -= 5
    glutPostRedisplay()

# ------------------ Main ------------------
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1200, 700)
    glutCreateWindow(b"Movimiento Parabolico - N Esferas (por nucleo) - Secuencial y Hilos")
    try:
        glutShowWindow()
    except:
        pass
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1)
    glPointSize(2.0)

    num_procesadores = multiprocessing.cpu_count()
    inicializar_esferas(num_esferas=num_procesadores)

    # imprimir parámetros
    print("\n=== PRIMERA SIMULACION: MODO SECUENCIAL ===")
    print(f"Numero de procesadores (esferas): {num_procesadores}")
    for i, e in enumerate(esferas):
        print(f"Esfera {i+1}: Ang={math.degrees(e.angulo):.1f}°, Vel={e.velocidad_inicial} m/s, X0={e.posicion[0]:.1f}")

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutTimerFunc(16, update, 0)
    glutIdleFunc(lambda: glutPostRedisplay())
    glutMainLoop()

if __name__ == "__main__":
    main()

