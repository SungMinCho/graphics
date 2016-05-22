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

isBspline = True
crossSections = [] # (list of CrossSection)
crossSectionsNum = 0
controlPointsNum = 0

catmullCrossSections = []

vertexNormals = {}

camera = Camera(Quaternion(1, 0, 0, 0), windowWidth, windowHeight)

class CrossSection:
    def mat_point(m, p):
        x = m[0][0]*p[0] + m[1][0]*p[1] + m[2][0]*p[2] + m[3][0]*p[3]
        y = m[0][1]*p[0] + m[1][1]*p[1] + m[2][1]*p[2] + m[3][1]*p[3]
        z = m[0][2]*p[0] + m[1][2]*p[1] + m[2][2]*p[2] + m[3][2]*p[3]
        w = m[0][3]*p[0] + m[1][3]*p[1] + m[2][3]*p[2] + m[3][3]*p[3]
        return (x, y, z, w)

    def __init__(self, controlPoints, scale, angle, axis, translation):
        self.controlPoints = controlPoints
        self.scale = scale
        self.angle = angle
        self.axis = axis
        self.translation = translation

        # calculate points on curve with the matrix multiplied
        realPoints = []
        for i in range(len(controlPoints)):
            p1 = controlPoints[i]
            p2 = controlPoints[(i+1) % len(controlPoints)]
            p3 = controlPoints[(i+2) % len(controlPoints)]
            p4 = controlPoints[(i+3) % len(controlPoints)]

            T = 5 # determines the number of knots
            for uI in range(0, T+1):
                u = uI / T
                u2 = u * u
                u3 = u2 * u

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

                realPoints.append((x, z))

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glPushMatrix()
        glTranslatef(translation.x, translation.y, translation.z)
        #glRotatef(angle, axis.x, axis.y, axis.z)
        glMultMatrixf(Quaternion.fromAxisAngle(axis, angle).makeRotationMatrix())
        glScalef(scale, scale, scale)
        m = glGetDoublev(GL_MODELVIEW_MATRIX)
        glPopMatrix()

        self.realPoints = [CrossSection.mat_point(m, (p[0], 0, p[1], 1)) for p in realPoints]


def crossSectionCatmullRom(c1, c2, c3, c4):
    T = 5 # determines the number of knots
    for uI in range(0, T+1):
        u = uI / T
        u2 = u*u
        u3 = u2*u

        f1 = -u3/2 + u2 - u/2
        f2 = u3*1.5 - u2*2.5 + 1
        f3 = -u3*1.5 + u2*2 + u/2
        f4 = u3/2 - u2/2

        # points
        ps1 = c1.controlPoints
        ps2 = c2.controlPoints
        ps3 = c3.controlPoints
        ps4 = c4.controlPoints

        if not (len(ps1) == len(ps2) and len(ps2) == len(ps3) and len(ps3) == len(ps4)):
            print('len', len(ps1), len(ps2), len(ps3), len(ps4))
            exit()

        ps = []
        for (p1, p2, p3, p4) in zip(ps1, ps2, ps3, ps4):
            (x1, z1) = p1
            (x2, z2) = p1
            (x3, z3) = p1
            (x4, z4) = p1

            x = f1*x1 + f2*x2 + f3*x3 + f4*x4
            z = f1*z1 + f2*z2 + f3*z3 + f4*z4

            ps.append((x, z))

        # scale
        scale = f1*c1.scale + f2*c2.scale + f3*c3.scale + f4*c4.scale

        # rotation
        angle = f1*c1.angle + f2*c2.angle + f3*c3.angle + f4*c4.angle
        axis = f1*c1.axis + f2*c2.axis + f3*c3.axis + f4*c4.axis


        # translation
        t1 = c1.translation
        t2 = c2.translation
        t3 = c3.translation
        t4 = c4.translation

        translation = f1*t1 + f2*t2 + f3*t3 + f4*t4

        yield CrossSection(ps, scale, angle, axis, translation)

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
                z = float(words.__next__())
                points.append((x, z))
            scale = float(words.__next__())

            angle = float(words.__next__())
            axisx = float(words.__next__())
            axisy = float(words.__next__())
            axisz = float(words.__next__())
            axis = Vector(axisx, axisy, axisz)

            positionx = float(words.__next__())
            positiony = float(words.__next__())
            positionz = float(words.__next__())
            translation = Vector(positionx, positiony, positionz)

            crossSection = CrossSection(points, scale, angle, axis, translation)

            crossSections.append(crossSection)

        first = crossSections[0]
        last = crossSections[-1]

        crossSections = [first, first, first] + crossSections + [last, last, last]

        global catmullCrossSections
        l = len(crossSections)
        for i in range(0, l-3): # (0,1,2,3) to (l-4,l-3,l-2,l-1)
            prev = None
            for c in crossSectionCatmullRom(crossSections[i], crossSections[i+1], crossSections[i+2], crossSections[i+3]):
                catmullCrossSections.append(c)
 
def drawMesh(c1, c2): # c1, c2 is CrossSection
    global vertexNormals

    glBegin(GL_TRIANGLE_STRIP)
    for (p1, p2) in list(zip(c1.realPoints, c2.realPoints)) + [(c1.realPoints[0], c2.realPoints[0])]:
        p1p = p1[0]
        p1n = p1[1]
        glNormal3f(p1n.x, p1n.y, p1n.z)
        glVertex3f(p1p[0], p1p[1], p1p[2])

        p2p = p2[0]
        p2n = p2[1]
        glNormal3f(p2n.x, p2n.y, p2n.z)
        glVertex3f(p2p[0], p2p[1], p2p[2])
    glEnd()

def pointToStlString(p):
    return str(p[0]) + " " + str(p[1]) + " " + str(p[2])

def appendNormals(c1, c2):
    global vertexNormals

    T1 = None
    T2 = c1.realPoints[0]
    T3 = c2.realPoints[0]
    index = 2
    for (p1, p2) in list(zip(c1.realPoints[1:], c2.realPoints[1:])) + [(c1.realPoints[0], c2.realPoints[0])]:
        (T1, T2, T3) = (T2, T3, p1)
        V = Vector(T2[0]-T1[0],T2[1]-T1[1],T2[2]-T1[2])
        W = Vector(T3[0]-T1[0],T3[1]-T1[1],T3[2]-T1[2])
        #N = Vector.cross(V, W)
        #N = (-N.x, -N.y, -N.z)
        N = Vector.cross(W, V)

        for p in (T1,T2,T3):
            if p not in vertexNormals:
                vertexNormals[p] = []
            vertexNormals[p].append(N)

        (T1, T2, T3) = (T2, T3, p2)
        V = Vector(T2[0]-T1[0],T2[1]-T1[1],T2[2]-T1[2])
        W = Vector(T3[0]-T1[0],T3[1]-T1[1],T3[2]-T1[2])
        N = Vector.cross(V, W)
        #N = (N.x, N.y, N.z)

        for p in (T1,T2,T3):
            if p not in vertexNormals:
                vertexNormals[p] = []
            vertexNormals[p].append(N)

def project():
    camera.lookat()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()

    camera.lookat()

    # draw the thing
    #for c in crossSections:
    #    closedCurve(c)

    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    l = len(catmullCrossSections)
    l = 1 / l
    (R, G, B) = (0, 1, 0)
    prev = None
    for c in catmullCrossSections:
        glColor3f(R,G,B)
        if prev == None:
            prev = c
            continue
        drawMesh(prev, c)
        prev = c
        R += l
        G -= l

    glFlush()
    glutSwapBuffers()

def preCalculateNormals(): # pre-calculate noramls and attach them to realpoints of crosssections
    global vertexNormals, catmullCrossSections

    prev = None
    for c in catmullCrossSections:
        if prev == None:
            prev = c
            continue
        appendNormals(prev, c)
        prev = c

    for k in vertexNormals:
        v = Vector(0,0,0)
        for n in vertexNormals[k]:
            v = v + n
        v = v.normalize()
        vertexNormals[k] = v

    for c in catmullCrossSections:
        for i in range(len(c.realPoints)):
            p = c.realPoints[i]
            if p in vertexNormals:
                v = vertexNormals[p]
            else:
                v = Vector(0,-1,0)
                assert(False)
            c.realPoints[i] = (p, v)


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

    parse()
    preCalculateNormals()

    mat_specular = [ 1.0, 1.0, 1.0, 1.0 ]
    mat_shininess = [ 50.0 ]
    light_position = [ -500.0, -500.0, 0.0, 0.0 ]
    light_position1 = [ 500.0, 500.0, 0.0, 0.0 ]
    light_position2 = [ 500.0, -500.0, 0.0, 0.0 ]
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glShadeModel(GL_SMOOTH);

    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glLightfv(GL_LIGHT1, GL_DIFFUSE, [1.0,0.0,0.2,1.0])
    glLightfv(GL_LIGHT1, GL_POSITION, light_position1)

    glLightfv(GL_LIGHT2, GL_DIFFUSE, [0.0,0.0,1.0,1.0])
    glLightfv(GL_LIGHT2, GL_POSITION, light_position2)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    glEnable(GL_DEPTH_TEST)
    """
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    la0 = [0.2,0.2,0.2,1.0]
    ld0 = [1.0,0.2,0.0,1.0]
    ls0 = [1.0,1.0,1.0,1.0]
    lp0 = [10.0,10.0,10.0,0]
    glLightfv(GL_LIGHT0, GL_AMBIENT, la0)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, ld0)
    glLightfv(GL_LIGHT0, GL_SPECULAR, ls0)
    glLightfv(GL_LIGHT0, GL_POSITION, lp0)
    """
    glutMainLoop()
    return 0

if __name__ == "__main__":
    main()
