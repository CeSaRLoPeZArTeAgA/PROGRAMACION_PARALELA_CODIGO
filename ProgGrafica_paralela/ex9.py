from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import math
import random
import threading
import multiprocessing
import time

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
    def __init__(self, color, angulo, velocidad_inicial, posicion_inicial):
        self.surface = Surface3D()
        self.surface.sphere_points(num_points=50000, radius=3)  # 50000 puntos como requiere el examen
        self.color = color
        self.angulo = math.radians(angulo)  # Convertir a radianes
        self.velocidad_inicial = velocidad_inicial
        self.posicion = posicion_inicial.copy()
        self.posicion_inicial = posicion_inicial.copy()  # Guardar posición inicial
        self.velocidad_x = velocidad_inicial * math.cos(self.angulo)
        self.velocidad_y = velocidad_inicial * math.sin(self.angulo)
        self.gravedad = -9.8
        self.tiempo = 0.0
        self.dt = 0.05  # Paso de tiempo
        self.activa = True
        self.lock = threading.Lock()  # Para sincronización thread-safe
    
    def actualizar(self):
        with self.lock:
            if not self.activa:
                return
                
            self.tiempo += self.dt
            
            # Movimiento parabólico desde la posición inicial
            self.posicion[0] = self.posicion_inicial[0] + self.velocidad_x * self.tiempo
            self.posicion[1] = self.posicion_inicial[1] + self.velocidad_y * self.tiempo + 0.5 * self.gravedad * self.tiempo**2
            
            # Si toca el suelo, detener la esfera
            if self.posicion[1] < 0:
                self.posicion[1] = 0
                self.activa = False
    
    def dibujar(self):
        with self.lock:
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
hilos = []
camera_pos = [50.0, 80.0, 200.0]  # Cámara ajustada para mejor vista
camera_target = [100.0, 40.0, 0.0]
detener_hilos = False
tiempo_inicio = 0
tiempo_fin = 0

def movimiento_esfera_hilo(esfera):
    """
    Función que ejecuta cada hilo para manejar el movimiento de una esfera
    """
    while not detener_hilos and esfera.activa:
        esfera.actualizar()
        time.sleep(0.016)  # ~60 FPS

def generar_color_aleatorio():
    """Genera un color RGB aleatorio"""
    return [random.random(), random.random(), random.random()]

def inicializar_esferas():
    """
    Inicializa las esferas según el número de núcleos del CPU
    Cada hilo maneja una esfera con parámetros aleatorios
    """
    global esferas, hilos, detener_hilos, tiempo_inicio
    
    # Detener hilos anteriores si existen
    detener_hilos = True
    for hilo in hilos:
        if hilo.is_alive():
            hilo.join()
    
    # Reiniciar variables
    detener_hilos = False
    esferas = []
    hilos = []
    
    # Obtener número de núcleos del CPU
    num_nucleos = multiprocessing.cpu_count()
    print(f"\n=== INICIALIZANDO {num_nucleos} ESFERAS (1 por núcleo) ===")
    
    # Crear esferas con parámetros aleatorios
    for i in range(num_nucleos):
        # Ángulo aleatorio entre 20° y 80°
        angulo = random.uniform(20, 80)
        
        # Velocidad aleatoria entre 20 m/s y 40 m/s
        velocidad = random.uniform(20, 40)
        
        # Color aleatorio
        color = generar_color_aleatorio()
        
        # Todas las esferas empiezan en el origen (0, 0, 0)
        posicion_inicial = [0, 0, 0]
        
        # Crear esfera
        esfera = Esfera(color, angulo, velocidad, posicion_inicial)
        esferas.append(esfera)
        
        print(f"Esfera {i+1}: Ángulo={angulo:.1f}°, Velocidad={velocidad:.1f} m/s")
        
        # Crear y arrancar hilo para esta esfera
        hilo = threading.Thread(target=movimiento_esfera_hilo, args=(esfera,), daemon=True)
        hilo.start()
        hilos.append(hilo)
    
    tiempo_inicio = time.time()
    print(f"\n{num_nucleos} hilos iniciados correctamente")
    print("Todas las esferas parten desde el origen (0, 0, 0)")
    print("Cada hilo controla el movimiento parabólico de una esfera\n")

def draw_axes(length=200.0):
    glLineWidth(3.0)
    glBegin(GL_LINES)

    # Eje X - rojo (ambos lados desde el origen)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-length, 0.0, 0.0)
    glVertex3f(length, 0.0, 0.0)

    # Eje Y - verde (hacia arriba desde el origen)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, 0, 0.0)
    glVertex3f(0.0, length, 0.0)

    # Eje Z - azul (ambos lados desde el origen)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, -length)
    glVertex3f(0.0, 0.0, length)

    glEnd()

def draw_ground():
    """Dibuja el plano del suelo - centrado y amplio para ambos lados"""
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(-300, 0, -150)
    glVertex3f(300, 0, -150)
    glVertex3f(300, 0, 150)
    glVertex3f(-300, 0, 150)
    glEnd()
    
    # Líneas de la cuadrícula
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_LINES)
    # Líneas paralelas al eje Z (verticales en vista superior)
    for i in range(-300, 301, 20):
        glVertex3f(i, 0.1, -150)
        glVertex3f(i, 0.1, 150)
    # Líneas paralelas al eje X (horizontales en vista superior)
    for i in range(-150, 151, 20):
        glVertex3f(-300, 0.1, i)
        glVertex3f(300, 0.1, i)
    glEnd()

def display_info():
    """Muestra información de las esferas en la ventana"""
    glColor3f(1.0, 1.0, 1.0)
    
    info = []
    activas = sum(1 for e in esferas if e.activa)
    info.append(f"=== ESFERAS: {len(esferas)} (1 por nucleo CPU) - Activas: {activas} ===")
    
    for i, esfera in enumerate(esferas[:10]):  # Mostrar solo las primeras 10 para no saturar
        estado = "ACTIVA" if esfera.activa else "REPOSO"
        info.append(f"E{i+1}: Ang={math.degrees(esfera.angulo):.1f}° Vel={esfera.velocidad_inicial:.1f}m/s - {estado}")
    
    if len(esferas) > 10:
        info.append(f"... y {len(esferas)-10} esferas mas")
    
    # Información de hilos
    hilos_activos = sum(1 for h in hilos if h.is_alive())
    info.append(f"\nHilos activos: {hilos_activos}/{len(hilos)}")
    
    # Instrucciones
    info.append("\nControles: Flechas-Mover camara | R-Reiniciar | ESC-Salir")
    
    for i, text in enumerate(info):
        glWindowPos2f(10, 680 - (i * 18))
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Configurar cámara
    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
              camera_target[0], camera_target[1], camera_target[2],
              0, 1, 0)

    # Dibujar elementos
    draw_axes(200)  # Ejes más largos
    draw_ground()
    
    # Dibujar esferas
    for esfera in esferas:
        esfera.dibujar()
    
    # Mostrar información
    display_info()
    
    glutSwapBuffers()

def update(value):
    # Verificar si todas las esferas están inactivas
    global tiempo_fin
    if all(not e.activa for e in esferas) and tiempo_fin == 0:
        tiempo_fin = time.time()
        tiempo_total = tiempo_fin - tiempo_inicio
        print(f"\n=== SIMULACION COMPLETADA ===")
        print(f"Tiempo total con hilos: {tiempo_total:.2f} segundos")
    
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)  # ~60 FPS

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / h if h != 0 else 1, 1, 1000)
    glMatrixMode(GL_MODELVIEW)

def keyboard(key, x, y):
    global camera_pos, camera_target, detener_hilos, tiempo_fin
    
    # Manejo de tecla ESC
    if ord(key) == 27:  # ESC
        detener_hilos = True
        for hilo in hilos:
            if hilo.is_alive():
                hilo.join(timeout=1)
        sys.exit(0)
    
    key = key.decode("utf-8").lower()
    
    # Reiniciar simulación
    if key == 'r':
        tiempo_fin = 0
        inicializar_esferas()
    
    glutPostRedisplay()

def special_keys(key, x, y):
    """Teclas especiales para rotar vista"""
    global camera_pos, camera_target
    
    if key == GLUT_KEY_LEFT:
        camera_pos[0] -= 10
        camera_target[0] -= 10
    elif key == GLUT_KEY_RIGHT:
        camera_pos[0] += 10
        camera_target[0] += 10
    elif key == GLUT_KEY_UP:
        camera_pos[1] += 10
        camera_target[1] += 10
    elif key == GLUT_KEY_DOWN:
        camera_pos[1] -= 10
        camera_target[1] -= 10
    
    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1200, 800)
    glutCreateWindow(b"Movimiento Parabolico - Threading Multi-Esfera")
    
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1)
    glPointSize(1.5)
    
    print("=" * 60)
    print("MOVIMIENTO PARABOLICO CON PROGRAMACION PARALELA")
    print("=" * 60)
    print(f"Nucleos del CPU detectados: {multiprocessing.cpu_count()}")
    print("Cada nucleo manejara una esfera con su propio hilo")
    print("Parametros: 50,000 puntos/esfera, angulos 20-80°, vel 20-40 m/s")
    print("=" * 60)
    
    # Inicializar esferas con threading
    inicializar_esferas()
    
    # Configurar callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutTimerFunc(16, update, 0)
    
    print("\n=== CONTROLES ===")
    print("Flechas: Mover camara")
    print("R: Reiniciar simulacion")
    print("ESC: Salir")
    
    glutMainLoop()

if __name__ == "__main__":
    main()