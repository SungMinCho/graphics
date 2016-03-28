from math import *
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

DEF_D = 5 # D degrees of rotation
dim = 200.0
windowName = b"window"
windowWidth = 1000
windowHeight = 800

toggleAxes = 0
toggleValues = 1
toggleMode = 0
th = 0
ph = 0
fov = 55
asp = 1

objId = 1

def Cos(th):
    return cos(pi/180*th)

def Sin(th):
    return sin(pi/180*th)

def project():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    if toggleMode:
        gluPerspective(fov, asp, dim/4, 4*dim)
    else:
        glOrtho(-dim*asp, +dim*asp, -dim, +dim, -dim, dim)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def setEye():
    if toggleMode:
        Ex = -2*dim*Sin(th)*Cos(ph)
        Ey = +2*dim        *Sin(ph)
        Ez = +2*dim*Cos(th)*Cos(ph)
        gluLookAt(Ex, Ey, Ez, 0, 0, 0, 0, Cos(ph), 0)
    else:
        glRotatef(ph, 1, 0, 0)
        glRotatef(th, 0, 1, 0)

def drawAxes():
    if toggleAxes:
        len = 200.0
        glColor3f(1, 1, 1)
        glBegin(GL_LINES)
        glColor3f(1,0,0)
        glVertex3d(0, 0, 0)
        glVertex3d(len, 0, 0)
        glColor3f(0,1,0)
        glVertex3d(0, 0, 0)
        glVertex3d(0, len, 0)
        glColor3f(0,0,1)
        glVertex3d(0, 0, 0)
        glVertex3d(0, 0, len)
        glEnd()
        # TODO print x y z glRasterPos

def drawValues():
    if toggleValues:
        glColor3f(0.8, 0.8, 0.8)
        # TODO printAt

def vertex(th2, ph2):
    x = Sin(th2)*Cos(ph2)
    y = Cos(th2)*Cos(ph2)
    z =          Sin(ph2)
    glVertex3d(x, y, z)

def drawLeaf(radius):
    r = radius
    glColor3f(0, 1, 0)
    glBegin(GL_QUAD_STRIP)
    glVertex3d(r, 0, r)
    glVertex3d(r, 2*r, r)
    glVertex3d(r, 0, -r)
    glVertex3d(r, 2*r, -r)
    glVertex3d(-r, 0, -r)
    glVertex3d(-r, 2*r, -r)
    glVertex3d(-r, 0, r)
    glVertex3d(-r, 2*r, r)
    glEnd()

    glBegin(GL_QUAD_STRIP)
    glVertex3d(r, 2*r, r)
    glVertex3d(r, 2*r, -r)
    glVertex3d(-r, 2*r, -r)
    glVertex3d(-r, 2*r, r)
    glEnd()

def drawCylinder(height, radius):
    glBegin(GL_QUAD_STRIP)
    for j in range(0, 361, DEF_D):
        glColor3f(139/255, 69/255, 19/255)
        glVertex3d(radius * Cos(j), height, radius * Sin(j))
        glColor3f(160/255, 82/255, 45/255)
        glVertex3d(radius*Cos(j), 0, radius*Sin(j))
    glEnd()

    for i in [height, 0]:
        glBegin(GL_TRIANGLE_FAN)
        glColor3f(0, 0, 1)
        glVertex3d(0, i, 0)
        for k in range(0, 361, DEF_D):
            glColor3f(0, 0.8, 1)
            glVertex3d(radius*Cos(k), i, radius*Sin(k))
        glEnd()

def drawTree(depth, height, radius):
    drawCylinder(height, radius)

    branches = 3

    for branch in range(branches):
        glPushMatrix()
        glTranslatef(0, height, 0)
        glRotatef(random.randint(-5, 5) + -60 + (120/(branches-1))*branch, 0, 0, 1)
        glRotatef(random.randint(-5, 5) + -90 + (180/(branches-1))*branch, 0, 1, 0)
        if depth:
            drawTree(depth - 1, height*3/4, radius/2)
        else:
            drawLeaf(radius)
        glPopMatrix()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()

    setEye()

    drawAxes()
    drawValues()

    drawTree(4, 50, 5)
    
    glFlush()
    glutSwapBuffers()

def reshape(width, height):
    asp = 1
    if height > 0:
        width / height
    glViewport(0, 0, width, height)
    project()

def windowKey(key, x, y):
    global objId, toggleAxes, toggleValues, toggleMode, fov, dim
    if key == b'\x1b':
        exit(0)
    elif key == b' ':
        if objId == 2:
            objId = 0
        else:
            objId += 1
    elif key == b'a':
        toggleAxes = 1 - toggleAxes
    elif key == b'v':
        toggleValues = 1 - toggleValues
    elif key == b'm':
        toggleMode = 1 - toggleMode
    elif key == b'i':
        fov -= 5
    elif key == b'o':
        fov += 5
    elif key == b'k':
        dim += 5
    elif key == b'l':
        dim -= 5

    project()
    glutPostRedisplay()

def windowSpecial(key, x, y):
    global th, ph
    if key == GLUT_KEY_RIGHT:
        th += 5
    elif key == GLUT_KEY_LEFT:
        th -= 5
    elif key == GLUT_KEY_UP:
        ph += 5
    elif key == GLUT_KEY_DOWN:
        ph -= 5

    th %= 360
    ph %= 360

    project()
    glutPostRedisplay()

def windowMenu(value):
    windowKey(chr(value), 0, 0)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(windowWidth, windowHeight)
    glutCreateWindow(windowName)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(windowKey)
    glutSpecialFunc(windowSpecial)
    glutCreateMenu(windowMenu)
    glutIdleFunc(display)
    #glutAddMenuEntry("Toggle Axes [a]", 'a')
    #glutAddMenuEntry("Toggle Values [v]", 'v')
    #glutAddMenuEntry("Toggle Mode [m]", 'm')
    #glutAttachMenu(GLUT_RIGHT_BUTTON)

    glutFullScreen()
    glutMainLoop()
    return 0

if __name__ == "__main__":
    main()
