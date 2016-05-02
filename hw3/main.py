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

class CrossSection:
    def __init__(self):
        self.controlPoints = []
        self.scale = 1
        self.rotation = None
        self.translation = (0, 0, 0)

isBspline = True
crossSections = [] # (list of CrossSection)
crossSectionsNum = 0
controlPointsNum = 0

def linesToStreamDisregardingComments(lines):
    for line in lines:
        sharpPos = line.find('#')
        if sharpPos >= 0:
            line = line[:sharpPos]
            line = ''.join(line)

        line = line.split()
        for word in line:
            if(word.startswith('#')):
                break
            if(word == ''):
                continue
            yield word

def parse():
    if(len(sys.argv) <= 1):
        print("usage : python3 main.py [inputfile path]")
        exit()

    filename = sys.argv[1]
    with open(filename, 'r') as f:
        words = linesToStreamDisregardingComments(f.readlines())

        global isBspline
        spline = words.__next__()
        if spline == "BSPLINE":
            isBspline = True
        elif spline == "CATMULL_ROM":
            isBspline = False
        else:
            print("spline should be either 'BSPLINE' or 'CATMULL_ROM'")
            exit()

        global crossSectionsNum
        global controlPointsNum
        crossSectionsNum = int(words.__next__())
        controlPointsNum = int(words.__next__())

        global crossSections
        for i in range(crossSectionsNum):
            points = []
            for j in range(controlPointsNum):
                x = float(words.__next__())
                y = float(words.__next__())
                points.append((x, y))
            scale = float(words.__next__())

            angle = float(words.__next__())
            axisx = float(words.__next__())
            axisy = float(words.__next__())
            axisz = float(words.__next__())
            rotation = (angle, axisx, axisy, axisz)

            positionx = float(words.__next__())
            positiony = float(words.__next__())
            positionz = float(words.__next__())
            translation = (positionx, positiony, positionz)

            crossSection = CrossSection()
            crossSection.controlPoints = points
            crossSection.scale = scale
            crossSection.rotation = rotation
            crossSection.translation = translation

            crossSections.append(crossSection)


def closedCurve(c): # c is of type CrossSection
    glPushMatrix()
    glScalef(c.scale, c.scale, c.scale)
    glRotatef(c.rotation[0], c.rotation[1], c.rotation[2], c.rotation[3])
    glTranslatef(c.translation[0], c.translation[1], c.translation[2])

    # control lines. for comparison with the actual curve
    for i in range(len(c.controlPoints)):
        glBegin(GL_LINE_STRIP)
        glColor3f(1, 1, 1)
        p = c.controlPoints[i]
        q = c.controlPoints[(i+1) % len(c.controlPoints)]
        glVertex3f(p[0], 0, p[1])
        glVertex3f(q[0], 0, q[1])
        glEnd()

    """for point in c.controlPoints:
        glBegin(GL_POINTS)
        glColor3f(0, 1, 0)
        #glPointSize(100)
        glVertex3f(point[0], 0, point[1])
        glEnd()"""

    glColor3f(0, 1, 0)

    for i in range(len(c.controlPoints)):
        p1 = c.controlPoints[i]
        p2 = c.controlPoints[(i+1) % len(c.controlPoints)]
        p3 = c.controlPoints[(i+2) % len(c.controlPoints)]
        p4 = c.controlPoints[(i+3) % len(c.controlPoints)]

        glBegin(GL_LINE_STRIP)
        T = 10
        for uI in range(0, T+1):
            u = uI / T
            u2 = u*u
            u3 = u2*u

            if isBspline:
                f1 = -u3/6 + u2/2 - u/2 + 1/6
                f2 = u3/2 - u2 + 2/3
                f3 = -u3/2 + u2/2 + u/2 + 1/6
                f4 = u3/6
            else:
                f1 = -u3/2 + u2 - u/2
                f2 = u3*1.5 - u2*2.5 + 1
                f3 = -u3*1.5 + u2*2 + u/2
                f4 = u3/2 - u2/2

            x = f1*p1[0] + f2*p2[0] + f3*p3[0] + f4*p4[0]
            z = f1*p1[1] + f2*p2[1] + f3*p3[1] + f4*p4[1]
            glVertex3f(x, 0, z)
        glEnd()


    glPopMatrix()

def project():
    camera.lookat()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()

    camera.lookat()

    # draw the thing
    for c in crossSections:
        closedCurve(c)
    
    glFlush()
    glutSwapBuffers()

def animate(value):
    glutPostRedisplay()
    glutTimerFunc(15, animate, 0)

def reshape(width, height):
    glViewport(0, 0, width, height)
    project()

def windowKey(key, x, y):
    global fov, dim, fovTarget, dimTarget, isBspline
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
        isBspline = not isBspline
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
    parse()
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
