from math import *
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from ironman import *
from DragHandler import *
from quaternion import *

windowName = b"window"
windowWidth = 1000
windowHeight = 600
th = 0
ph = 0
fov = 55
dim = 90.0
fovTarget = 55
dimTarget = 90.0
asp = windowWidth / windowHeight

ironman = IronMan()
dragHandler = DragHandler(Quaternion(1, 0, 0, 0), windowWidth, windowHeight)

def project():
    setEye()


def setEye():
    Ex = -2*dim*Sin(th)*Cos(ph)
    Ey = +2*dim        *Sin(ph)
    Ez = +2*dim*Cos(th)*Cos(ph)
    gluLookAt(Ex, Ey, Ez, 0, 0, 0, 0, Cos(ph), 0)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fov, asp, dim/4, 4*dim)
    glTranslatef(dragHandler.cameraOffsetX, dragHandler.cameraOffsetY, 0)

    glMatrixMode(GL_MODELVIEW)

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

    global fov, dim
    if fov < fovTarget:
        if fovTarget - fov < 5:
            fov = fovTarget
        else:
            fov += 2
    elif fov > fovTarget:
        if fov - fovTarget < 5:
            fov = fovTarget
        else:
            fov -= 2

    if dim < dimTarget:
        if dimTarget - dim < 10:
            dim = dimTarget
        else:
            dim += 2
    elif dim > dimTarget:
        if dim - dimTarget < 10:
            dim = dimTarget
        else:
            dim -= 2

    glutPostRedisplay()
    glutTimerFunc(15, animate, 0)

def reshape(width, height):
    glViewport(0, 0, width, height)
    project()

def windowKey(key, x, y):
    global fov, dim, fovTarget, dimTarget
    if key == b'\x1b':
        exit(0)
    if key == b'i':
        fov = min(fov+5, 175)
        fovTarget = fov
    if key == b'o':
        fov = max(fov-5, 5)
        fovTarget = fov
    if key == b'k':
        dim += 10
        dimTarget = dim
    if key == b'l':
        dim = max(dim-10, 10)
        dimTarget = dim
    if key == b's':
        dragHandler.cameraOffsetInit()
        fovTarget = 55
        dimTarget = 90
        # TODO. this should do see all
    project()

def windowMenu(value):
    windowKey(chr(value), 0, 0)

def mouseEvent(button, state, x, y):
    if state == GLUT_UP:
        dragHandler.mouseWasUp = True
    if state == GLUT_DOWN:
        if button == GLUT_LEFT_BUTTON:
            dragHandler.mouseLeft = True
        else:
            dragHandler.mouseLeft = False

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
