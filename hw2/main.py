from math import *
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from ironman import *
from DragHandler import *
from quaternion import *

dim = 90.0
windowName = b"window"
windowWidth = 1000
windowHeight = 600
th = 0
ph = 0
fov = 55
asp = 1

ironman = IronMan()
dragHandler = DragHandler(Quaternion(1, 0, 0, 0), windowWidth, windowHeight)

def project():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    gluPerspective(fov, asp, dim/4, 4*dim)

    glMatrixMode(GL_MODELVIEW)

    setEye()


def setEye():
    Ex = -2*dim*Sin(th)*Cos(ph)
    Ey = +2*dim        *Sin(ph)
    Ez = +2*dim*Cos(th)*Cos(ph)
    gluLookAt(Ex, Ey, Ez, 0, 0, 0, 0, Cos(ph), 0)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()

    setEye()

    m = Quaternion.makeRotationMatrix(dragHandler.orientation)
    glMultMatrixf(m)
    ironman.draw()

    glFlush()
    glutSwapBuffers()

def animate(value):
    ironman.tick()
    glutPostRedisplay()
    glutTimerFunc(15, animate, 0)

def reshape(width, height):
    glViewport(0, 0, width, height)
    project()

def windowKey(key, x, y):
    global fov, dim
    if key == b'\x1b':
        exit(0)
    if key == b'q':
        fov = min(fov+5, 175)
    if key == b'w':
        fov = max(fov-5, 5)
    if key == b'a':
        dim += 10
    if key == b's':
        dim = max(dim-10, 10)
    project()

def windowMenu(value):
    windowKey(chr(value), 0, 0)

def mouseEvent(button, state, x, y):
    if state == GLUT_UP:
        dragHandler.mouseWasUp = True

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(windowWidth, windowHeight)
    glutCreateWindow(windowName)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(windowKey)
    glutMouseFunc(mouseEvent)
    glutMotionFunc(dragHandler.drag)
    glutCreateMenu(windowMenu)
    glutTimerFunc(15, animate, 0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #glutFullScreen()
    glutMainLoop()
    return 0

if __name__ == "__main__":
    main()
