from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from quaternion import *
from math import *

class DragHandler:
    def __init__(self, orientation, screenwidth, screenheight):
        self.orientation = orientation
        self.mouseWasUp = True
        self.mouseLeft = True
        self.centerx = screenwidth/2
        self.centery = screenheight/2
        self.radius = min(screenwidth, screenheight)/3
        self.radiusSqr = self.radius * self.radius

        self.cameraOffsetX = 0
        self.cameraOffsetY = 0

    def vectorFromXY(self, x, y):
        x -= self.centerx
        y -= self.centery
        #print(x, y)
        r1_aux = x*x + y*y  # TODO when out of range.
        if r1_aux >= self.radiusSqr:
            v = Vector(x, y, 0)
            v = Vector.normalize(v)
            v = Vector.scale(self.radius, v)
            return v
        r1 = sqrt(r1_aux)
        z = sqrt(self.radiusSqr - r1_aux)
        return Vector(x, y, z)

    def dragLeft(self, x, y):
        if self.mouseWasUp:
            self.mouseWasUp = False
            self.lastv = self.vectorFromXY(x, y)
            return

        # calculate v1 by lastx, lasty
        v1 = self.lastv

        # calculate v2 by x, y
        v2 = self.vectorFromXY(x, y)

        self.lastv = v2

        # calculate n = v1 x v2
        n = Vector.cross(v2, v1)
        if n.length() == 0:
            return

        # n = rotate n by orientation
        #n = Quaternion.rotateVector(self.orientation, n)

        # rotation = fromAxisAngle(normalize(v3'), v3'.length())
        angle = acos(Vector.dot(Vector.normalize(v1), Vector.normalize(v2)))
        rotation = Quaternion.fromAxisAngle(Vector.normalize(n), angle)
        # orientation = rotation * orientation
        self.orientation = Quaternion.mult(rotation, self.orientation)

        self.lastv = v2

    def dragRight(self, x, y):
        if self.mouseWasUp:
            self.mouseWasUp = False
            self.lastx = x
            self.lasty = y
            return
        self.cameraOffsetX += x - self.lastx
        self.cameraOffsetY -= y - self.lasty
        self.lastx = x
        self.lasty = y

    def cameraOffsetInit(self):
        self.cameraOffsetX = 0
        self.cameraOffsetY = 0

    def drag(self, x, y):
        if self.mouseLeft:
            self.dragLeft(x, y)
        else:
            self.dragRight(x, y)
