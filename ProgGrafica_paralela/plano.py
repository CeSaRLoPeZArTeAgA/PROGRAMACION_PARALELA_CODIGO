from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def init():
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0, 0.1, 100.0)

def draw_grid():
    glColor3f(0.6, 0.6, 0.6)
    for i in range(-5, 6):
        glBegin(GL_LINES)
        glVertex3f(i, 0, -5)
        glVertex3f(i, 0, 5)
        glVertex3f(-5, 0, i)
        glVertex3f(5, 0, i)
        glEnd()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(5, 5, 5, 0, 0, 0, 0, 1, 0)  # Vista isométrica

    draw_grid()

    glFlush()
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(600, 600)
    glutCreateWindow(b"Plano Cartesiano 2D")
    #glutCreateWindow("Plano Cartesiano 2D")
    init()
    glutDisplayFunc(display)
    glutMainLoop()

if __name__ == '__main__':
    main()
