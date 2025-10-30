from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import math
import random
import multiprocessing
import time
import threading
import matplotlib.pyplot as plt 

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
            phi = math.acos(2 * random.uniform(0, 1) - 1)
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            self.points.append(Point3D(x, y, z))

class Esfera:
    def __init__(self, color, angulo, velocidad_inicial):
        self.surface = Surface3D()
        self.surface.sphere_points(num_points=50000, radius=3)
        self.color = color
        self.angulo = math.radians(angulo)
        self.velocidad_inicial = velocidad_inicial
        self.posicion = [0.0, 0.0, 0.0]
        self.velocidad_x = velocidad_inicial * math.cos(self.angulo)
        self.velocidad_y = velocidad_inicial * math.sin(self.angulo)
        self.gravedad = -9.8
        self.tiempo = 0.0
        self.dt = 0.05
        self.activa = True
    
    def actualizar(self):
        if not self.activa:
            return
        self.tiempo += self.dt
        self.posicion[0] = self.velocidad_x * self.tiempo
        self.posicion[1] = self.velocidad_y * self.tiempo + 0.5 * self.gravedad * self.tiempo**2
        if self.posicion[1] < 0:
            self.posicion[1] = 0
            self.activa = False
    
    def dibujar(self):
        glPushMatrix()
        glTranslatef(self.posicion[0], self.posicion[1], self.posicion[2])
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

# variables para la segunda pasada con hilos
initial_params = []
threaded_pass_started = False
thread_pool = []
mode = "SECUENCIAL"

# variable globales para guardar tiempos
tiempos_vuelo_secuencial = {}
tiempos_vuelo_hilos = {}

# ===========================================================
def inicializar_esferas():
    global esferas, initial_params, threaded_pass_started, mode, tiempos_inicio, tiempos_final
    esferas = []
    
    # Esfera 1
    # se escoge angulo aleatorio entre [20°,80°] 
    ang1 = random.randint(20, 80)
    v1 = random.randint(20, 40)
    esfera1 = Esfera([1.0, 0.0, 0.0], ang1, v1)
    esfera1.posicion = [-15, 0, 0]
    
    # Esfera 2
    # se escoge angulo aleatorio entre [20°,80°]
    ang2 = random.randint(20, 80)
    v2 = random.randint(20, 40)
    esfera2 = Esfera([0.0, 0.0, 1.0], ang2, v2)
    esfera2.posicion = [15, 0, 0]
    
    esferas = [esfera1, esfera2]
    
    # registrar tiempos de inicio
    tiempos_inicio = {i: time.time() for i in range(len(esferas))}
    tiempos_final = {i: None for i in range(len(esferas))}
    initial_params = [(ang1, v1), (ang2, v2)]
    threaded_pass_started = False
    mode = "SECUENCIAL"

# ===========================================================
# generacion del plano del suelo
def draw_ground():
    #dibuja el plano del suelo
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(-50, 0, -50)
    glVertex3f(150, 0, -50)
    glVertex3f(150, 0, 50)
    glVertex3f(-50, 0, 50)
    glEnd()
    # Líneas de la cuadrícula
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_LINES)
    # Líneas paralelas al eje Z (variando X)
    for x in range(-50, 151, 10):
        glVertex3f(x, 0.001, -50)
        glVertex3f(x, 0.001, 50)
    # Líneas paralelas al eje X (variando Z)
    for z in range(-50, 51, 10):
        glVertex3f(-50, 0.001, z)
        glVertex3f(150, 0.001, z)
    glEnd()

# ===========================================================
# generacion de ejes coordenadas
def draw_axes(length=100.0):
    glLineWidth(2.0)
    glBegin(GL_LINES)
    
    # Eje X - rojo
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-length, 0.15, 0.0)
    glVertex3f(3*length, 0.15, 0.0)
    
    # Eje Y - verde
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0, -length*0.1, 0.0)
    glVertex3f(0, length*0.8, 0.0)
    
    # Eje Z - azul
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.15, -length)
    glVertex3f(0.0, 0.15, length)
    
    glEnd()

# ===========================================================
# impresion de la informacion de las esferas en la ventana usuario
def display_info():
    glColor3f(1.0, 1.0, 1.0)
    
    info = ["MOVIMIENTO DE ESFERAS USANDO PARALELISMO rev2.2", ""]
    for i, esfera in enumerate(esferas):
        estado = "ACTIVA" if esfera.activa else "REPOSO"
        info.append(f"Esfera {i+1}: Ang={math.degrees(esfera.angulo):.1f}°, Vel={esfera.velocidad_inicial:.1f} m/s - {estado}")
    # Instrucciones
    info += ["", "Controles: X,Y,Z - Mover camara | R - Reiniciar",
             f"Camara: ({camera_pos[0]:.1f}, {camera_pos[1]:.1f}, {camera_pos[2]:.1f})", "",
             f"Modo: {mode}"]
    
    for i, text in enumerate(info):
        glWindowPos2f(10, 580 - (i * 20))
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))
    
    # mostrar tiempos en pantalla
    for i, esfera in enumerate(esferas):
        if i in tiempos_inicio:
            if tiempos_final[i] is None:
                duracion = time.time() - tiempos_inicio[i]
                texto = f"Esfera {i+1}: {duracion:.2f} s (en vuelo)"
            else:
                duracion = tiempos_final[i] - tiempos_inicio[i]
                texto = f"Esfera {i+1}: {duracion:.2f} s (finalizada)"
            glWindowPos2f(10, 580 - ((len(info)+1 + i) * 20))
            for char in texto:
                glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))

# ===========================================================
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # configurar camara
    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
              camera_target[0], camera_target[1], camera_target[2],
              0, 1, 0)
    
    # dibujar elementos
    draw_ground()
    draw_axes(50)
    for esfera in esferas:
        esfera.dibujar()
        
    # mostrar informacion
    display_info()
    
    glutSwapBuffers()

# ===========================================================
def run_threaded_simulation_visible(params_list):
    global esferas, threaded_pass_started, mode, tiempos_inicio, tiempos_final, thread_pool, tiempos_vuelo_hilos
    esferas = []
    for (ang, vel), posx in zip(params_list, [-15, 15]):
        e = Esfera([1.0, 0.0, 0.0] if posx < 0 else [0.0, 0.0, 1.0], ang, vel)
        e.posicion = [posx, 0, 0]
        esferas.append(e)
    tiempos_inicio = {i: time.time() for i in range(len(esferas))}
    tiempos_final = {i: None for i in range(len(esferas))}
    thread_pool = []
    mode = "HILOS"
    threaded_pass_started = True

    def mover_y_actualizar(esfera_obj, idx):
        while esfera_obj.activa:
            esfera_obj.actualizar()
            time.sleep(esfera_obj.dt)
        tiempos_final[idx] = time.time()

    for i, e in enumerate(esferas):
        t = threading.Thread(target=mover_y_actualizar, args=(e, i), daemon=True)
        thread_pool.append(t)
        t.start()

    def refrescar_visual(_=0):
        glutPostRedisplay()
        activo = any(e.activa for e in esferas)
        if activo:
            glutTimerFunc(16, refrescar_visual, 0)
        else:
            for i in range(len(esferas)):
                if tiempos_final[i] is None:
                    tiempos_final[i] = time.time()
                dur = tiempos_final[i] - tiempos_inicio[i]
                tiempos_vuelo_hilos[i] = dur
                print(f"[HILOS] Esfera {i+1} tiempo vuelo = {dur:.3f} s")
            
            #calcular la aceleracion de proceso
            if tiempos_vuelo_secuencial:
                print("\n=== RESULTADOS DE ACEL. PROCESO X USAR HILOS ===")
                for i in tiempos_vuelo_secuencial:
                    t_seq = tiempos_vuelo_secuencial[i]
                    t_thr = tiempos_vuelo_hilos.get(i, t_seq)
                    speedup = t_seq / t_thr if t_thr > 0 else 0
                    print(f"Esfera {i+1}: Acel. = {speedup:.2f}x")

    glutTimerFunc(16, refrescar_visual, 0)

# ===========================================================
def update(value):
    global tiempos_inicio, tiempos_final, threaded_pass_started, initial_params, mode, tiempos_vuelo_secuencial
    
    alguna_activa = False
    
    # actualizacion fisica de las esferas guardando el indice
    for i, esfera in enumerate(esferas):
        esfera.actualizar()
        if esfera.activa:
            alguna_activa = True
        else:
            # solo registrar/print cuando estamos en modo SECUENCIAL
            if i in tiempos_final and tiempos_final[i] is None:
                tiempos_final[i] = time.time()
                duracion = tiempos_final[i] - tiempos_inicio.get(i, tiempos_final[i])
                if mode == "SECUENCIAL":
                    tiempos_vuelo_secuencial[i] = duracion
                    print(f"Esfera {i+1} finalizó en {duracion:.2f} segundos.")
                    # si estamos en HILOS, no hacemos el print/guardado aqui
                    
    glutPostRedisplay()
    
    # si todas terminaron y no se inició la pasada con hilos, lanzarla (visible)
    if (not alguna_activa) and (not threaded_pass_started) and (mode == "SECUENCIAL"):
        params_copy = list(initial_params)
        run_threaded_simulation_visible(params_copy)
    glutTimerFunc(16, update, 0)

# ===========================================================
def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / h if h != 0 else 1, 1, 1000)
    glMatrixMode(GL_MODELVIEW)

def keyboard(key, x, y):
    global camera_pos, camera_target, threaded_pass_started, mode
    
    key = key.decode("utf-8").lower()
    
     # mover camara en eje X
    if key == 'x':
        camera_pos[0] += 5
        camera_target[0] += 5
    
    # mover camara en eje Y
    elif key == 'y':
        camera_pos[1] += 5
        camera_target[1] += 5
        
    # mover camara en eje Z 
    elif key == 'z':
        camera_pos[2] += 5
        camera_target[2] += 5
        
    # reiniciar simulacion 
    elif key == 'r':
        inicializar_esferas()
        print("\n====================================================")
        print("============ REINICIO DE SIMULACIÓN ============")
        print("\n==== PARAMETROS ESFERAS EN CONSOLA ====")
        for i, esfera in enumerate(esferas):
            print(f"Esfera {i+1}: Angulo={math.degrees(esfera.angulo):.1f}°, Velocidad={esfera.velocidad_inicial} m/s")
        threaded_pass_started = False
        mode = "SECUENCIAL"
        
    # teclas adicionales para mas control    
    elif key == 'a':# Acercar
        camera_pos[2] -= 5
    elif key == 's':# Alejar
        camera_pos[2] += 5
        
    glutPostRedisplay()

# teclas especiales para rotar vista
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
 
# ===========================================================
# grafica estadisticas de la simulacion
def mostrar_graficos():
    if not tiempos_vuelo_secuencial or not tiempos_vuelo_hilos:
        print("No hay datos de tiempo para graficar.")
        return

    etiquetas = [f"Esfera {i+1}" for i in tiempos_vuelo_secuencial]
    valores_seq = [tiempos_vuelo_secuencial[i] for i in tiempos_vuelo_secuencial]
    valores_thr = [tiempos_vuelo_hilos.get(i, 0) for i in tiempos_vuelo_hilos]

    # Grafico 1: comparacion individual por esfera  
    prom_seq = sum(valores_seq) / len(valores_seq)
    prom_thr = sum(valores_thr) / len(valores_thr)

    plt.figure(figsize=(6, 5))
    plt.bar(["Secuencial", "Hilos"], [prom_seq, prom_thr],
            color=["orange", "skyblue"], width=0.5)
    plt.ylabel("Tiempo promedio (s)")
    plt.title("Comparación de promedio de tiempos de simulación")
    plt.tight_layout()
    plt.show()   
    
    # Grafico 2: promedios de tiempos
    plt.figure(figsize=(8, 5))
    x = range(len(etiquetas))
    plt.bar(x, valores_seq, width=0.4, label='Secuencial', align='center')
    plt.bar([i + 0.4 for i in x], valores_thr, width=0.4, label='Hilos', align='center')
    plt.xticks([i + 0.2 for i in x], etiquetas)
    plt.ylabel("Tiempo de vuelo (s)")
    plt.title("Comparación de tiempos por esfera")
    plt.legend()
    plt.tight_layout()
    plt.show()
    
# ===========================================================
# inicializacion
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 700)
    glutCreateWindow(b"Practica 3 Paralela:  Movimiento Parabolico - 2 Esferas 3D")
    try:
        glutShowWindow()
    except:
        pass
    
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1)
    glPointSize(2.0)
    
    inicializar_esferas()
    
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutTimerFunc(16, update, 0)
    glutIdleFunc(lambda: glutPostRedisplay())
    glutCloseFunc(mostrar_graficos)  
    
    print("\n====================================================")
    print("============== PRIMERA DE SIMULACIÓN ==============")
    print("\n=== IMPRESION DE PARAMETROS Y CONTROLES EN CONSOLA ===")
    num_procesadores = multiprocessing.cpu_count()
    print(f"Numero de procesadores: {num_procesadores}")
    print("X, Y, Z: Mover cámara en ejes")
    print("A, S: Acercar/Alejar cámara")
    print("R: Reiniciar simulación")
    print("Flechas: Rotar vista")
    print("\n==== PARAMETROS ESFERAS EN CONSOLA ====")
    for i, esfera in enumerate(esferas):
        print(f"Esfera {i+1}: Angulo={math.degrees(esfera.angulo):.1f}°, Velocidad={esfera.velocidad_inicial} m/s")
    
    glutMainLoop()

# ===========================================================
if __name__ == "__main__":
    main()