# UA1 - Hermite Curve in Python with Mouse Clicks (pygame version)

import pygame
from pygame.locals import *
from OpenGL.GL import *
import numpy as np

window_width, window_height = 800, 600
points = []

def hermite(p0, p1, m0, m1, t):
    h00 = 2*t**3 - 3*t**2 + 1
    h10 = t**3 - 2*t**2 + t
    h01 = -2*t**3 + 3*t**2
    h11 = t**3 - t**2
    return h00*p0 + h10*m0 + h01*p1 + h11*m1

def estimate_tangents(pts):
    tangents = []
    for i in range(len(pts)):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == len(pts) - 1:
            t = pts[-1] - pts[-2]
        else:
            t = (pts[i+1] - pts[i-1]) / 2
        tangents.append(t)
    return tangents

def draw():
    glClear(GL_COLOR_BUFFER_BIT)

    # Draw points
    glPointSize(6)
    glColor3f(1, 0, 0)
    glBegin(GL_POINTS)
    for p in points:
        glVertex2f(p[0], p[1])
    glEnd()

    # Draw Hermite curve
    if len(points) >= 2:
        tangents = estimate_tangents(np.array(points))
        glColor3f(0, 1, 0)
        glLineWidth(2)
        glBegin(GL_LINE_STRIP)
        for i in range(len(points) - 1):
            p0 = np.array(points[i])
            p1 = np.array(points[i+1])
            m0 = tangents[i]
            m1 = tangents[i+1]
            for t in np.linspace(0, 1, 50):
                pt = hermite(p0, p1, m0, m1, t)
                glVertex2f(pt[0], pt[1])
        glEnd()

    pygame.display.flip()

def main():
    pygame.init()
    pygame.display.set_mode((window_width, window_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Curva de Hermite - pygame")

    glClearColor(0, 0, 0, 1)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, window_width, 0, window_height, -1, 1)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                screen_y = window_height - y
                points.append([x, screen_y])

        draw()

    pygame.quit()

if __name__ == '__main__':
    main()
