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

isBspline = True
crossSections = [] # (list of (points, scale, rotation, translation))
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

            crossSections.append((points, scale, rotation, translation))


def closedCurve(points, scale, rotation, translation):
    if isBspline:
        pass
    else:
        pass

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
    parse()
    print(crossSections)
    return
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
