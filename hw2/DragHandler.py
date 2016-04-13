from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from quaternion import *
from math import *

class DragHandler:
    def __init__(self, orientation, screenwidth, screenheight):
        self.orientation = orientation
        self.mouseWasUp = True
        self.centerx = screenwidth/2
        self.centery = screenheight/2
        self.radius = min(screenwidth, screenheight)/2
        self.radiusSqr = self.radius * self.radius

    def vectorFromXY(self, x, y):
        x -= self.centerx
        y -= self.centery
        #print(x, y)
        r1_aux = x*x + y*y  # TODO when out of range.
        r1 = sqrt(r1_aux)
        z = sqrt(self.radiusSqr - r1_aux)
        return Vector(x, y, z)

    def drag(self, x, y):
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
        n = Vector.cross(v1, v2)
        if n.length() == 0:
            return

        # n = rotate n by orientation
        #n = Quaternion.rotateVector(self.orientation, n)

        # rotation = fromAxisAngle(normalize(v3'), v3'.length())
        rotation = Quaternion.fromAxisAngle(Vector.normalize(n), n.length()/50000)
        # orientation = rotation * orientation
        self.orientation = Quaternion.mult(rotation, self.orientation)

        self.lastv = v2
