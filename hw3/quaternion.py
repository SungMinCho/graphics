from math import *

class Vector:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	def add(v1, v2):
		return Vector(v1.x+v2.x, v1.y+v2.y, v1.z+v2.z)

	def sub(v1, v2):
		return Vector(v1.x-v2.x, v1.y-v2.y, v1.z-v2.z)

	def scale(c, v):
		return Vector(c*v.x, c*v.y, c*v.z)

	def dot(v1, v2):
		return v1.x*v2.x + v1.y*v2.y + v1.z*v2.z

	def cross(a, b):
		return Vector(a.y*b.z - a.z*b.y, a.x*b.z - a.z*b.x, a.x*b.y - a.y*b.x)

	def length(self):
		return sqrt(Vector.dot(self, self))

	def normalize(v):
		return Vector.scale(1/v.length(), v)

class Quaternion:
	def __init__(self, w, x, y, z):
		self.w = w
		self.x = x
		self.y = y
		self.z = z

	def fromAxisAngle(axis, angle):
		return Quaternion(cos(angle/2.0), axis.x*sin(angle/2.0), axis.y*sin(angle/2.0), axis.z*sin(angle/2.0))

	def mult(a, b):
		return Quaternion(a.w*b.w - a.x*b.x - a.y*b.y - a.z*b.z,
                      a.w*b.x + a.x*b.w + a.y*b.z - a.z*b.y,
                      a.w*b.y - a.x*b.z + a.y*b.w + a.z*b.x,
                      a.w*b.z + a.x*b.y - a.y*b.x + a.z*b.w)

	def conjugate(q):
		return Quaternion(q.w, -q.x, -q.y, -q.z)

	def rotateVector(q, v):
		vq = Quaternion(0, v.x, v.y, v.z)
		vq = Quaternion.mult(q, vq)
		vq = Quaternion.mult(vq, Quaternion.conjugate(q))
		return Vector(vq.x, vq.y, vq.z)

	def makeRotationMatrix(q):
		x = Vector(1, 0, 0)
		y = Vector(0, 1, 0)
		z = Vector(0, 0, 1)
		xt = Quaternion.rotateVector(q, x)
		yt = Quaternion.rotateVector(q, y)
		zt = Quaternion.rotateVector(q, z)

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


