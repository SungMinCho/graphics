from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from quaternion import *
from math import *

class Camera:
    # eye = focus + (0, 0, dim) * orientation
    def __init__(self, orientation, width, height):
        self.dim = 120
        self.fov = 55
        self.asp = width / height
        self.orientation = orientation
        self.focus = Vector(0, 0, 0)
        self.camera = self.focus + self.orientation.rotateVector(Vector(0, 0, self.dim))
        self.up = self.orientation.rotateVector(Vector(0, 1, 0))
        self.zNear = self.dim/4
        self.zFar = self.dim*4

        self.centerx = width/2
        self.centery = height/2
        self.radius = min(width, height)/3
        self.radiusSqr = self.radius * self.radius
        self.mouseWasUp = True
        self.mouseLeft = True

    def vectorFromXY(self, x, y):
        x -= self.centerx
        #x = -x
        y -= self.centery
        r1_aux = x*x + y*y
        if r1_aux >= self.radiusSqr:
            v = Vector(x, y, 0)
            v = v.normalize()
            v = self.radius * v
            return v
        r1 = sqrt(r1_aux)
        z = sqrt(self.radiusSqr - r1_aux)
        return Vector(x, y, z)

    def lookat(self):
        gluLookAt(self.camera.x, self.camera.y, self.camera.z,
                    self.focus.x, self.focus.y, self.focus.z,
                    self.up.x, self.up.y, self.up.z)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.asp, self.zNear, self.zFar)

        glMatrixMode(GL_MODELVIEW)

    def dragLeft(self, x, y):
        if self.mouseWasUp:
            self.mouseWasUp = False
            self.lastv = self.vectorFromXY(x, y)
            return

        v1 = self.lastv
        v2 = self.vectorFromXY(x, y)
        self.lastv = v2
        n = Vector.cross(v1, v2)
        n.y = -n.y
        if n.length() == 0:
            return
        n = self.orientation.rotateVector(n)
        angle = acos(Vector.dot(v1.normalize(), v2.normalize()))
        rotation = Quaternion.fromAxisAngle(Vector.normalize(n), angle)
        self.orientation = rotation * self.orientation

        self.camera = self.focus + self.orientation.rotateVector(Vector(0, 0, self.dim))
        self.up = self.orientation.rotateVector(Vector(0, 1, 0))

    def dragRight(self, x, y):
        if self.mouseWasUp:
            self.mouseWasUp = False
            self.lastx = x
            self.lasty = y
            return

        right = Vector(1, 0, 0)
        right = self.orientation.rotateVector(right)
        up = Vector(0, 1, 0)
        up = self.orientation.rotateVector(up)

        self.focus = self.focus + (-(x-self.lastx) * right)
        self.focus = self.focus + ((y-self.lasty) * up)

        self.lastx = x
        self.lasty = y

        self.camera = self.focus + self.orientation.rotateVector(Vector(0, 0, self.dim))

    def drag(self, x, y):
        if self.mouseLeft:
            self.dragLeft(x, y)
        else:
            self.dragRight(x, y)

    def reset(self):
        self.focus = Vector(0, 0, 0)
        self.camera = self.focus + self.orientation.rotateVector(Vector(0, 0, self.dim))
        self.fov = 55

    def dolly(self, distance):
        direction = Vector(0, 0, -1)
        direction = self.orientation.rotateVector(direction)
        direction = distance * direction
        self.focus = self.focus + direction
        self.camera = self.camera + direction

    def zoom(self, angle):
        self.fov += angle
        if self.fov >= 180:
            self.fov = 179
        if self.fov <= 0:
            self.fov = 1

    def seek(self, x, y, points):
        mindist = 99999999999999999
        targetpoint = None
        for point in points:
            dist = (point[0] - x)*(point[0] - x) + (point[1] + y)*(point[1] + y) # reverse y because opengl is y= 0 at bottom
            if dist < mindist:
                mindist = dist
                targetpoint = point
        (px, py, pz) = gluUnProject(targetpoint[0], targetpoint[1], targetpoint[2])
        self.focus = Vector(px, py, pz)
        self.camera = self.focus + self.orientation.rotateVector(Vector(0, 0, self.dim))
