from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import math
import random

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
        self.surface.sphere_points(num_points=2000, radius=3)
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

# Variables globales
esferas = []
camera_pos = [0.0, 50.0, 100.0]
camera_target = [50.0, 25.0, 0.0]

def inicializar_esferas():
    global esferas
    esferas = []
    
    # Esfera 1: Ángulo 45°, velocidad 30
    esfera1 = Esfera(color=[1.0, 0.0, 0.0], angulo=45, velocidad_inicial=30)
    esfera1.posicion = [-15, 0, 0]  # Posición inicial diferente en X
    
    # Esfera 2: Ángulo 60°, velocidad 25
    esfera2 = Esfera(color=[0.0, 0.0, 1.0], angulo=60, velocidad_inicial=25)
    esfera2.posicion = [15, 0, 0]
    
    esferas = [esfera1, esfera2]

def draw_axes(length=100.0):
    glLineWidth(2.0)
    glBegin(GL_LINES)

    # Eje X - rojo
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-length, 0.0, 0.0)
    glVertex3f(length, 0.0, 0.0)

    # Eje Y - verde
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, -length, 0.0)
    glVertex3f(0.0, length, 0.0)

    # Eje Z - azul
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, -length)
    glVertex3f(0.0, 0.0, length)

    glEnd()

def draw_ground():
    """Dibuja el plano del suelo"""
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(-100, 0, -100)
    glVertex3f(100, 0, -100)
    glVertex3f(100, 0, 100)
    glVertex3f(-100, 0, 100)
    glEnd()
    
    # Líneas de la cuadrícula
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_LINES)
    for i in range(-100, 101, 10):
        glVertex3f(i, 0.1, -100)
        glVertex3f(i, 0.1, 100)
        glVertex3f(-100, 0.1, i)
        glVertex3f(100, 0.1, i)
    glEnd()

def display_info():
    """Muestra información de las esferas en la ventana"""
    glColor3f(1.0, 1.0, 1.0)
    
    info = []
    for i, esfera in enumerate(esferas):
        estado = "ACTIVA" if esfera.activa else "REPOSO"
        info.append(f"Esfera {i+1}: Ang={math.degrees(esfera.angulo):.1f}°, Vel={esfera.velocidad_inicial:.1f} m/s - {estado}")
    
    # Instrucciones
    info.append("Controles: X,Y,Z - Mover camara | R - Reiniciar")
    info.append(f"Camara: ({camera_pos[0]:.1f}, {camera_pos[1]:.1f}, {camera_pos[2]:.1f})")
    
    for i, text in enumerate(info):
        glWindowPos2f(10, 580 - (i * 20))
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char)) # type: ignore

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Configurar cámara
    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
              camera_target[0], camera_target[1], camera_target[2],
              0, 1, 0)

    # Dibujar elementos
    draw_axes(50)
    draw_ground()
    
    # Dibujar esferas
    for esfera in esferas:
        esfera.dibujar()
    
    # Mostrar información
    display_info()
    
    glutSwapBuffers()

def update(value):
    # Actualizar física de las esferas
    for esfera in esferas:
        esfera.actualizar()
    
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)  # ~60 FPS

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

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 700)
    glutCreateWindow(b"Movimiento Parabolico - 2 Esferas 3D")
    
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1)
    glPointSize(2.0)
    
    # Inicializar esferas
    inicializar_esferas()
    
    # Configurar callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutTimerFunc(16, update, 0)
    
    print("=== CONTROLES ===")
    print("X, Y, Z: Mover cámara en ejes")
    print("A, S: Acercar/Alejar cámara")
    print("R: Reiniciar simulación")
    print("Flechas: Rotar vista")
    print("\n=== PARÁMETROS ESFERAS ===")
    for i, esfera in enumerate(esferas):
        print(f"Esfera {i+1}: Angulo={math.degrees(esfera.angulo):.1f}°, Velocidad={esfera.velocidad_inicial} m/s")
    
    glutMainLoop()

if __name__ == "__main__":
    main()