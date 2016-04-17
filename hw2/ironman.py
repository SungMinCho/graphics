from math import *
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

DEF_D = 5

points = []

def Cos(th):
    return cos(pi/180*th)

def Sin(th):
    return sin(pi/180*th)

def drawCylinder(height, radius, r, g, b, r2, g2, b2):
    global points
    points.append(gluProject(0, 0, 0))
    points.append(gluProject(0, height, 0))
    glColor3f(r, g, b)
    glBegin(GL_QUAD_STRIP)
    for j in range(0, 361, DEF_D):
        glVertex3d(radius * Cos(j), height, radius * Sin(j))
        glVertex3d(radius*Cos(j), 0, radius*Sin(j))
    glEnd()

    glColor3f(r2, g2, b2)
    for i in [height, 0]:
        glBegin(GL_TRIANGLE_FAN)
        glVertex3d(0, i, 0)
        for k in range(0, 361, DEF_D):
            glVertex3d(radius*Cos(k), i, radius*Sin(k))
        glEnd()

def drawStand(a1, b1, a2, b2, h, r, g, b):
    global points
    for i in [0, 0.2, 0.4, 0.6, 0.8, 1]:
        x = a1*i + a2*(1-i)
        y = h*i
        z = b1*i + b2*(1-i)
        points.append(gluProject(x, y, z))
        points.append(gluProject(x, y, -z))
        points.append(gluProject(-x, y, z))
        points.append(gluProject(-x, y, -z))
        points.append(gluProject(0, y, 0))

    glColor3f(r, g, b)
    glBegin(GL_QUAD_STRIP)
    glVertex3d(a1, h, b1)
    glVertex3d(a2, 0, b2)
    glVertex3d(a1, h, -b1)
    glVertex3d(a2, 0, -b2)
    glVertex3d(-a1, h, -b1)
    glVertex3d(-a2, 0, -b2)
    glVertex3d(-a1, h, b1)
    glVertex3d(-a2, 0, b2)
    glVertex3d(a1, h, b1)
    glVertex3d(a2, 0, b2)
    glEnd()

    glBegin(GL_QUAD_STRIP)
    glVertex3d(a1, h, b1)
    glVertex3d(a1, h, -b1)
    glVertex3d(-a1, h, b1)
    glVertex3d(-a1, h, -b1)
    glEnd()

    glBegin(GL_QUAD_STRIP)
    glVertex3d(a2, 0, b2)
    glVertex3d(a2, 0, -b2)
    glVertex3d(-a2, 0, b2)
    glVertex3d(-a2, 0, -b2)
    glEnd()

class IronMan:
    def init(self):
        global th, ph
        self.rightArmAngle1 = 10
        self.rightArmAngle2 = 30
        self.rightArmFingerAngle = 90
        self.rightArmLaserLength = 1
        self.rightArmBounce = 0
        self.leftArmAngle1 = 10
        self.leftArmAngle2 = 30
        self.air = 15

    def init_leg(self):
        self.rightLegAngle1 = 30
        self.rightLegAngle2 = -10
        self.leftLegAngle1 = -10
        self.leftLegAngle2 = -10

    def __init__(self):
        self.init()
        self.init_leg()
        self.points = None

    def tick(self):
        return
        global th, ph
        if self.rightArmAngle1 >= 90:
            if self.rightArmAngle2 <= 0:
                if self.rightArmFingerAngle > 0:
                    self.rightArmFingerAngle -= 5
                else:
                    if self.rightArmLaserLength >= 500:
                        self.init()
                        self.init_leg()
                    else:
                        self.rightArmLaserLength += 25
                        if self.rightArmBounce == 2:
                            self.rightArmBounce = 0
                        else:
                            self.rightArmBounce = 2 
            else:
                self.rightArmAngle2 -= 3
                self.leftLegAngle2 -= 0.5
                self.air += 1
                #ph -= 1
                #th -= 1
        else:
            self.rightArmAngle1 += 3
            self.leftArmAngle1 -= 3
            self.leftLegAngle1 -= 2
            self.rightLegAngle1 -= 2
            self.air += 1
            #ph -= 1
            #th -= 1

    def drawHead(self):
        drawStand(7, 5, 7, 5, 17, 1, 0, 0)
        
        glColor3f(1, 1, 0)
        glBegin(GL_QUAD_STRIP)
        glVertex3d(-7, 17, 5.1)
        glVertex3d(7, 17, 5.1)
        glVertex3d(-7, 0, 5.1)
        glVertex3d(7, 0, 5.1)
        glEnd()

        glBegin(GL_QUAD_STRIP)
        glVertex3d(7, 17.1, 5.1)
        glVertex3d(3, 17.1, 5.1)
        glVertex3d(7, 17.1, 0)
        glVertex3d(3, 17.1, 0)
        glEnd()

        glBegin(GL_QUAD_STRIP)
        glVertex3d(-7, 17.1, 5.1)
        glVertex3d(-3, 17.1, 5.1)
        glVertex3d(-7, 17.1, 0)
        glVertex3d(-3, 17.1, 0)
        glEnd()

        glColor3f(0, 0, 0)
        glBegin(GL_QUAD_STRIP)
        glVertex3d(-5.2, 10.2, 5.15) 
        glVertex3d(-0.8, 10.2, 5.15) 
        glVertex3d(-5.2, 6, 5.15) 
        glVertex3d(-0.8, 6, 5.15) 
        glEnd()

        glColor3f(0, 0, 0)
        glBegin(GL_QUAD_STRIP)
        glVertex3d(5.2, 10.2, 5.15) 
        glVertex3d(0.8, 10.2, 5.15) 
        glVertex3d(5.2, 6, 5.15) 
        glVertex3d(0.8, 6, 5.15) 
        glEnd()


        glColor3f(1, 1, 1)
        glBegin(GL_QUAD_STRIP)
        glVertex3d(-5, 10, 5.2) 
        glVertex3d(-1, 10, 5.2) 
        glVertex3d(-5, 6, 5.2) 
        glVertex3d(-1, 6, 5.2) 
        glEnd()

        glColor3f(1, 1, 1)
        glBegin(GL_QUAD_STRIP)
        glVertex3d(5, 10, 5.2) 
        glVertex3d(1, 10, 5.2) 
        glVertex3d(5, 6, 5.2) 
        glVertex3d(1, 6, 5.2) 
        glEnd()

    def drawBody(self):
        glPushMatrix()
        glTranslatef(0, -30, 0)
        drawStand(9, 5, 9, 5, 30, 1, 0, 0)

        glPushMatrix()
        glTranslatef(0, 25, 0)
        glRotatef(90, 1, 0, 0)
        drawCylinder(7, 3, 1, 1, 1, 1, 1, 1)
        glPopMatrix()
        glPopMatrix()

    def drawRightArm(self):
        glPushMatrix()
        glTranslatef(-(9 + 3), 0, 0)
        glRotatef(180, 0, 0, 1)
        glTranslatef(0,0, -self.rightArmBounce)
        glRotatef(self.rightArmAngle1, 1, 0, 0)
        drawStand(3, 3, 3, 3, 20, 1, 1, 0)

        glPushMatrix()
        glTranslatef(0, 20, 0)
        glRotatef(self.rightArmAngle2, 1, 0, 0)
        drawStand(3, 3, 3, 3, 15, 1, 0, 0)

        glPushMatrix()
        glTranslatef(0, 15, 0)

        glPushMatrix()
        glTranslatef(0, 0, 2)
        drawStand(3, 4, 3, 4, 3, 1, 0, 0)

        glPushMatrix()
        glRotatef(90, 0, 0, 1)
        glTranslatef(1.5, 3, 0) 
        glRotatef(-self.rightArmFingerAngle, 0, 0, 1)
        drawCylinder(3, 2, 1, 1, 0, 1, 1, 0)
        glTranslatef(0, 3, 0)
        glRotatef(-self.rightArmFingerAngle, 0, 0, 1)
        drawCylinder(3, 2, 1, 0, 0, 1, 0, 0)
        glPopMatrix()

        glRotatef(90, 1, 0, 0)
        glTranslatef(3, 4, -1.5)

        for finger in range(3):
            glPushMatrix()
            glTranslatef(-finger*3, 0, 0)
            glRotatef(-self.rightArmFingerAngle, 1, 0, 0)
            drawCylinder(5, 1, 1, 1, 0, 1, 1, 0)
            glTranslatef(0, 5, 0)
            glRotatef(-self.rightArmFingerAngle, 1, 0, 0)
            drawCylinder(5, 1, 1, 0, 0, 1, 0, 0)
            glPopMatrix()

        glPopMatrix()

        glTranslatef(0, 3, 0)
        drawCylinder(self.rightArmLaserLength, 2, 0, 1, 1, 0, 1, 1)
        glPopMatrix()
        glPopMatrix()
        glPopMatrix()

    def drawLeftArm(self):
        glPushMatrix()
        glTranslatef((9 + 3), 0, 0)
        glRotatef(180, 0, 0, 1)
        glRotatef(self.leftArmAngle1, 1, 0, 0)
        drawStand(3, 3, 3, 3, 20, 1, 1, 0)

        glPushMatrix()
        glTranslatef(0, 20, 0)
        glRotatef(self.leftArmAngle2, 1, 0, 0)
        drawStand(3, 3, 3, 3, 15, 1, 0, 0)
        glPopMatrix()

        glPopMatrix()

    def drawLeftLeg(self):
        glPushMatrix()
        glTranslatef(9-4, -30, 0)
        glRotatef(180, 0, 0, 1)
        glRotatef(self.leftLegAngle1, 1, 0, 0)
        drawStand(4, 4, 4, 4, 20, 1, 1, 0) 
        glTranslatef(0, 20, 0)
        glRotatef(self.leftLegAngle2, 1, 0, 0)
        drawStand(4, 4, 4, 4, 20, 1, 0, 0)
        glPopMatrix()

    def drawRightLeg(self):
        glPushMatrix()
        glTranslatef(-(9-4), -30, 0)
        glRotatef(180, 0, 0, 1)
        glRotatef(self.rightLegAngle1, 1, 0, 0)
        drawStand(4, 4, 4, 4, 20, 1, 1, 0)
        glTranslatef(0, 20, 0)
        glRotatef(self.rightLegAngle2, 1, 0, 0)
        drawStand(4, 4, 4, 4, 20, 1, 0, 0)
        glPopMatrix()

    def draw(self):
        global points
        points = []
        glPushMatrix()
        glTranslatef(0, self.air, 0)
        #glScalef(1, 1, 1)
        self.drawHead()
        self.drawBody()
        self.drawRightArm()
        self.drawLeftArm()
        self.drawLeftLeg()
        self.drawRightLeg()
        glPopMatrix()
        self.points = points
        #print(len(self.points))

