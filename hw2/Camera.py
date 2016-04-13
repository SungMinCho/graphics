from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from quaternion import *
from math import *

class Camera:
	# eye = focus + (0, 0, dim) * orientation
	def __init__(self, orientation, width, height):
		self.dim = 180.0
		self.fov = 55
		self.asp = width / height
		self.orientation = orientation
		self.focus = Vector(0, 0, 0)
		self.camera = Vector.add(self.focus, Quaternion.rotateVector(self.orientation, Vector(0, 0, self.dim)))
		self.up = Quaternion.rotateVector(self.orientation, Vector(0, 1, 0))
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
		y -= self.centery
		r1_aux = x*x + y*y
		if r1_aux >= self.radiusSqr:
			v = Vector(x, y, 0)
			v = Vector.normalize(v)
			v = Vector.scale(self.radius, v)
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
		if n.length() == 0:
			return
		n = Quaternion.rotateVector(self.orientation, n)
		angle = acos(Vector.dot(Vector.normalize(v1), Vector.normalize(v2)))
		rotation = Quaternion.fromAxisAngle(Vector.normalize(n), angle)
		self.orientation = Quaternion.mult(rotation, self.orientation)

		self.camera = Vector.add(self.focus, Quaternion.rotateVector(self.orientation, Vector(0, 0, self.dim)))
		self.up = Quaternion.rotateVector(self.orientation, Vector(0, 1, 0))

	def dragRight(self, x, y):
		if self.mouseWasUp:
			self.mouseWasUp = False
			self.lastx = x
			self.lasty = y
			return

		right = Vector(1, 0, 0)
		right = Quaternion.rotateVector(self.orientation, right)
		up = Vector(0, 1, 0)
		up = Quaternion.rotateVector(self.orientation, up)

		self.focus = Vector.add(self.focus, Vector.scale(-(x-self.lastx), right))
		self.focus = Vector.add(self.focus, Vector.scale(y-self.lasty, up))

		self.lastx = x
		self.lasty = y

		self.camera = Vector.add(self.focus, Quaternion.rotateVector(self.orientation, Vector(0, 0, self.dim)))

	def drag(self, x, y):
		if self.mouseLeft:
			self.dragLeft(x, y)
		else:
			self.dragRight(x, y)

	def reset(self):
		self.camera = Vector(0, 0, self.dim)
		self.up = Vector(0, 1, 0)
		self.focus = Vector(0, 0, 0)

	def dolly(self, distance):
		direction = Vector(0, 0, -1)
		direction = Quaternion.rotateVector(self.orientation, direction)
		direction = Vector.scale(distance, direction)
		self.focus = Vector.add(self.focus, direction)
		self.camera = Vector.add(self.camera, direction)

	def zoom(self, angle):
		self.fov += angle
		if self.fov > 180:
			self.fov = 179
		if self.fov < 0:
			self.fov = 1
