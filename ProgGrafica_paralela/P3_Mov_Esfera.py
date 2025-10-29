from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import math
import random
import multiprocessing
import time

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
        self.surface.sphere_points(num_points=500, radius=3)
        self.color = color
        self.angulo = math.radians(angulo)  # Convertir a radianes
        self.velocidad_inicial = velocidad_inicial
        self.posicion = [0.0, 0.0, 0.0]
        self.velocidad_x = velocidad_inicial * math.cos(self.angulo)
        self.velocidad_y = velocidad_inicial * math.sin(self.angulo)
        self.gravedad = -9.8
        self.tiempo = 0.0
        self.dt = 0.05  # Paso de tiempo
        self.activa = True
    
    def actualizar(self):
        if not self.activa:
            return
            
        self.tiempo += self.dt
        
        # Movimiento parabólico
        self.posicion[0] = self.velocidad_x * self.tiempo
        self.posicion[1] = self.velocidad_y * self.tiempo + 0.5 * self.gravedad * self.tiempo**2
        
        # Si toca el suelo, detener la esfera
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

# ===========================================================
def inicializar_esferas():
    global esferas
    esferas = []
    
    # Esfera 1: 
    # se escoge angulo aleatorio entre [20°,80°] 
    # se escoge velocidad aleatoria entre [20m/s,40m/s] 
    esfera1 = Esfera(color=[1.0, 0.0, 0.0], angulo= random.randint(20, 80), velocidad_inicial=random.randint(20, 40))
    esfera1.posicion = [-15, 0, 0]  # Posición inicial diferente en X
    
    
    # Esfera 2:
    # se escoge angulo aleatorio entre [20°,80°] 
    # se escoge velocidad aleatoria entre [20m/s,40m/s] 
    esfera2 = Esfera(color=[0.0, 0.0, 1.0], angulo= random.randint(20, 80), velocidad_inicial=random.randint(20, 40))
    esfera2.posicion = [15, 0, 0]
    
    esferas = [esfera1, esfera2]
    
    # Registrar tiempos de inicio
    global tiempos_inicio, tiempos_final
    tiempos_inicio = {i: time.time() for i in range(len(esferas))}
    tiempos_final = {i: None for i in range(len(esferas))}

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
    
    info = []
    info.append("MOVIMIENTO DE ESFERAS  ")
    info.append("")
    for i, esfera in enumerate(esferas):
        estado = "ACTIVA" if esfera.activa else "REPOSO"
        info.append(f"Esfera {i+1}: Ang={math.degrees(esfera.angulo):.1f}°, Vel={esfera.velocidad_inicial:.1f} m/s - {estado}")
    
    # Instrucciones
    info.append("")
    info.append("Controles: X,Y,Z - Mover camara | R - Reiniciar")
    info.append(f"Camara: ({camera_pos[0]:.1f}, {camera_pos[1]:.1f}, {camera_pos[2]:.1f})")
    
    for i, text in enumerate(info):
        glWindowPos2f(10, 580 - (i * 20))
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char)) # type: ignore
            
    # mostrar tiempos en pantalla
    y_offset = 150
    for i, esfera in enumerate(esferas):
        if i in tiempos_inicio:
            if tiempos_final[i] is None:
                duracion = time.time() - tiempos_inicio[i]
                texto = f"Esfera {i+1}: {duracion:.2f} s (en vuelo)"
            else:
                duracion = tiempos_final[i] - tiempos_inicio[i]
                texto = f"Esfera {i+1}: {duracion:.2f} s (finalizada)"
            glWindowPos2f(10, 580 - (len(info)*20 + (i*20)))
            for char in texto:
                glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))
                
# ===========================================================
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Configurar cámara
    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
              camera_target[0], camera_target[1], camera_target[2],
              0, 1, 0)
    
    # Dibujar elementos
    draw_ground()
    draw_axes(50)
    
    # Dibujar esferas
    for esfera in esferas:
        esfera.dibujar()
    
    # Mostrar información
    display_info()
    
    glutSwapBuffers()

# ===========================================================

def update(value):
    global tiempos_inicio, tiempos_final

    alguna_activa = False

    # Actualizar física de las esferas guardando el índice correctamente
    for i, esfera in enumerate(esferas):
        esfera.actualizar()

        # Si la esfera sigue activa, marcamos la bandera
        if esfera.activa:
            alguna_activa = True
        else:
            # Si ya está en reposo y aún no guardamos su tiempo final, guardarlo
            if i in tiempos_final and tiempos_final[i] is None:
                # Guardamos el tiempo absoluto de finalización y mostramos en consola
                tiempos_final[i] = time.time()
                duracion = tiempos_final[i] - tiempos_inicio.get(i, tiempos_final[i])
                # impresion en consola
                print(f"Esfera {i+1} finalizó en {duracion:.2f} segundos.")

    # Siempre redibujar (evita "congelamiento" visual)
    glutPostRedisplay()

    # Seguir llamando al timer mientras haya al menos una esfera activa
    # Si quieres que el timer continúe siempre (independiente de actividad), quita la condición
    if alguna_activa:
        glutTimerFunc(16, update, 0)
    else:
        # Todas las esferas terminaron; aun así forzamos un último redraw
        glutTimerFunc(16, update, 0)

    

# ===========================================================  

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / h if h != 0 else 1, 1, 1000)
    glMatrixMode(GL_MODELVIEW)

def keyboard(key, x, y):
    global camera_pos, camera_target
    
    key = key.decode("utf-8").lower()
    
    # Mover cámara en eje X
    if key == 'x':
        camera_pos[0] += 5
        camera_target[0] += 5
    
    # Mover cámara en eje Y
    elif key == 'y':
        camera_pos[1] += 5
        camera_target[1] += 5
    
    # Mover cámara en eje Z
    elif key == 'z':
        camera_pos[2] += 5
        camera_target[2] += 5
    
    # Reiniciar simulación
    elif key == 'r':
        inicializar_esferas()
        print("\n====================================================")
        print("\n=== REINICIO DE SIMULACIÓN ===")
        print("\n=== PARAMETROS ESFERAS EN CONSOLA ===")
        for i, esfera in enumerate(esferas):
            print(f"Esfera {i+1}: Angulo={math.degrees(esfera.angulo):.1f}°, Velocidad={esfera.velocidad_inicial} m/s")
        print("\n=== TIEMPOS FINALES DE LAS ESFERAS EN CONSOLA ===")
    
    # Teclas adicionales para más control
    elif key == 'a':  # Acercar
        camera_pos[2] -= 5
    elif key == 's':  # Alejar
        camera_pos[2] += 5
    
    glutPostRedisplay()

def special_keys(key, x, y):
    """Teclas especiales para rotar vista"""
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
# inicializacion
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 700)
    glutCreateWindow(b"Practica 3 Paralela:  Movimiento Parabolico - 2 Esferas 3D")
    
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1)
    glPointSize(2.0)
    
    # experimento usando codificacion normal 
    inicializar_esferas()
    
    # Configurar callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutTimerFunc(16, update, 0)
    
    print("\n\n=== IMPRESION DE PARAMETROS DE EXPERIMETOS EN CONSOLA ===")
    # Número de procesadores disponibles
    num_procesadores = multiprocessing.cpu_count()
    print(f"Numero de procesadores: {num_procesadores}")
    
    print("\n=== IMPRESION DE CONTROLES EN CONSOLA ===")
    print("X, Y, Z: Mover cámara en ejes")
    print("A, S: Acercar/Alejar cámara")
    print("R: Reiniciar simulación")
    print("Flechas: Rotar vista")
    print("\n=== PARAMETROS ESFERAS EN CONSOLA ===")
    for i, esfera in enumerate(esferas):
        print(f"Esfera {i+1}: Angulo={math.degrees(esfera.angulo):.1f}°, Velocidad={esfera.velocidad_inicial} m/s")
    print("\n=== TIEMPOS FINALES DE LAS ESFERAS EN CONSOLA ===")
    
    glutMainLoop()
    

# ===========================================================
# ejecucion principal
if __name__ == "__main__":
    main()