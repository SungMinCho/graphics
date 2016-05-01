from math import *
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from quaternion import *
from Camera import *

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

camera = Camera(Quaternion(1, 0, 0, 0), windowWidth, windowHeight)

def project():
    camera.lookat()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()

    camera.lookat()

    # draw the thing
    
    glFlush()
    glutSwapBuffers()

def animate(value):
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
        camera.zoom(5)
    if key == b'o':
        camera.zoom(-5)
    if key == b'k':
        camera.dolly(-10)
    if key == b'l':
        camera.dolly(10)
    if key == b'r':
        camera.reset()
    if key == b's':
        pass
    project()

def windowMenu(value):
    windowKey(chr(value), 0, 0)

def mouseEvent(button, state, x, y):
    if state == GLUT_UP:
        camera.mouseWasUp = True
    if state == GLUT_DOWN:
        if button == GLUT_LEFT_BUTTON:
            camera.mouseLeft = True
        elif button == GLUT_RIGHT_BUTTON:
            camera.mouseLeft = False

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(windowWidth, windowHeight)
    glutCreateWindow(windowName)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(windowKey)
    glutMouseFunc(mouseEvent)
    glutMotionFunc(camera.drag)
    glutCreateMenu(windowMenu)
    glutTimerFunc(15, animate, 0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glutMainLoop()
    return 0

if __name__ == "__main__":
    main()
