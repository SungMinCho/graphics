from math import *

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, v2):
        return Vector(self.x+v2.x, self.y+v2.y, self.z+v2.z)

    def __sub__(self, v2):
        return Vector(self.x-v2.x, self.y-v2.y, self.z-v2.z)

    def __mul__(self, c):
        return Vector(c*self.x, c*self.y, c*self.z)

    def __rmul__(self, c):
        return Vector(c*self.x, c*self.y, c*self.z)

    def dot(v1, v2):
        return v1.x*v2.x + v1.y*v2.y + v1.z*v2.z

    def cross(a, b):
        return Vector(a.y*b.z - a.z*b.y, a.x*b.z - a.z*b.x, a.x*b.y - a.y*b.x)

    def length(self):
        return sqrt(Vector.dot(self, self))

    def normalize(self):
        return (1/self.length()) * self

class Quaternion:
    def __init__(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def fromAxisAngle(axis, angle):
        return Quaternion(cos(angle/2.0), axis.x*sin(angle/2.0), axis.y*sin(angle/2.0), axis.z*sin(angle/2.0))

    def __mul__(self, b):
        return Quaternion(self.w*b.w - self.x*b.x - self.y*b.y - self.z*b.z,
                          self.w*b.x + self.x*b.w + self.y*b.z - self.z*b.y,
                          self.w*b.y - self.x*b.z + self.y*b.w + self.z*b.x,
                          self.w*b.z + self.x*b.y - self.y*b.x + self.z*b.w)


    def conjugate(self):
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def rotateVector(self, v):
        vq = Quaternion(0, v.x, v.y, v.z)
        vq = self * vq * self.conjugate()
        return Vector(vq.x, vq.y, vq.z)

    def makeRotationMatrix(self):
        x = Vector(1, 0, 0)
        y = Vector(0, 1, 0)
        z = Vector(0, 0, 1)
        xt = self.rotateVector(x)
        yt = self.rotateVector(y)
        zt = self.rotateVector(z)

        m = [0] * 16

        m[0] = Vector.dot(x, xt)
        m[1] = Vector.dot(y, xt)
        m[2] = Vector.dot(z, xt)
        m[3] = 0

        m[4] = Vector.dot(x, yt)
        m[5] = Vector.dot(y, yt)
        m[6] = Vector.dot(z, yt)
        m[7] = 0

        m[8] = Vector.dot(x, zt)
        m[9] = Vector.dot(y, zt)
        m[10] = Vector.dot(z, zt)
        m[11] = 0

        m[12] = 0
        m[13] = 0
        m[14] = 0
        m[15] = 1

        return m


