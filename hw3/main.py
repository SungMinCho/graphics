from math import *
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from quaternion import *
from Camera import *
import copy

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

focussection = 0
focussectionpoint = 0

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

        self.orientation = Quaternion.fromAxisAngle(axis, angle)

        self.update()

    def update(self):
        # calculate points on curve with the matrix multiplied
        realPoints = []
        for i in range(len(self.controlPoints)):
            p1 = self.controlPoints[i]
            p2 = self.controlPoints[(i+1) % len(self.controlPoints)]
            p3 = self.controlPoints[(i+2) % len(self.controlPoints)]
            p4 = self.controlPoints[(i+3) % len(self.controlPoints)]

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
        glTranslatef(self.translation.x, self.translation.y, self.translation.z)
        glRotatef(self.angle, self.axis.x, self.axis.y, self.axis.z)
        glScalef(self.scale, self.scale, self.scale)
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

def updateCrossSections():
    global catmullCrossSections

    cs = copy.deepcopy(crossSections)
    cs = [cs[0]] + cs + [cs[-1]]

    catmullCrossSections = []
    l = len(cs)
    for i in range(0, l-3): # (0,1,2,3) to (l-4,l-3,l-2,l-1)
        for c in crossSectionCatmullRom(cs[i], cs[i+1], cs[i+2], cs[i+3]):
            catmullCrossSections.append(c)

def init():
    global crossSections
    first = CrossSection([(0,0),(10,0),(10,10),(0,10)], 1, 0, Vector(1, 0, 0), Vector(0, 0, 0))
    crossSections.append(first)

def drawMesh(c1, c2): # c1, c2 is CrossSection
    glBegin(GL_TRIANGLE_STRIP)
    for (p1, p2) in list(zip(c1.realPoints, c2.realPoints)) + [(c1.realPoints[0], c2.realPoints[0])]:
        glVertex3f(p1[0], p1[1], p1[2])
        glVertex3f(p2[0], p2[1], p2[2])
    glEnd()


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

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    l = len(catmullCrossSections)
    if l != 0:
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

def animate(value):
    glutPostRedisplay()
    glutTimerFunc(15, animate, 0)

def reshape(width, height):
    glViewport(0, 0, width, height)
    project()

def windowKey(key, x, y):
    global fov, dim, fovTarget, dimTarget, isBspline, crossSections, focussection, focussectionpoint
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
    if key == b'c':
        crossSections.append(copy.deepcopy(crossSections[-1]))
        last = crossSections[-1]
        v = last.orientation.rotateVector(Vector(0, 1, 0))
        last.translation = last.translation + v
        focussection = len(crossSections) - 1
        focussectionpoint = 0
        crossSections[-1].update()
        updateCrossSections()
        #glutPostRedisplay()
    if key == b'p':
        focussectionpoint += 1
    if key == b'q':
        focussection -= 1
    if key == b'e':
        focussection += 1
    if key == b'w':
        c = crossSections[focussection]
        v = c.orientation.rotateVector(Vector(0, 1, 0))
        c.translation = c.translation + v
        c.update()
        updateCrossSections()
    if key == b's':
        c = crossSections[focussection]
        v = c.orientation.rotateVector(Vector(0, -1, 0))
        c.translation = c.translation + v
        c.update()
        updateCrossSections()
    if key == b'a':
        c = crossSections[focussection]
        v = c.orientation.rotateVector(Vector(-1, 0, 0))
        c.translation = c.translation + v
        c.update()
        updateCrossSections()
    if key == b'd':
        c = crossSections[focussection]
        v = c.orientation.rotateVector(Vector(1, 0, 0))
        c.translation = c.translation + v
        c.update()
        updateCrossSections()
    if key == b'z':
        c = crossSections[focussection]
        v = c.orientation.rotateVector(Vector(0, 0, 1))
        c.translation = c.translation + v
        c.update()
        updateCrossSections()
    if key == b'x':
        c = crossSections[focussection]
        v = c.orientation.rotateVector(Vector(0, 0, -1))
        c.translation = c.translation + v
        c.update()
        updateCrossSections()

    glutPostRedisplay()
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

    init()

    glutMainLoop()
    return 0

if __name__ == "__main__":
    main()
