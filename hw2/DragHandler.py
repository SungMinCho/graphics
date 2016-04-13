from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from quaternion import *

class DragHandler:
    def __init__(self, orientation):
        self.orientation = orientation
        self.mouseWasUp = True

    def drag(self, x, y):
        if self.mouseWasUp:
            self.mouseWasUp = False
            self.lastx = x
            self.lasty = y
            return
        print(x-self.lastx, y-self.lasty)

        glMatrixMode(GL_MODELVIEW)
        #glLoadIdentity()

        glRotatef(self.lastx - x, 0, 0, 1)
        glRotatef(self.lasty - y, 1, 0, 0)

        self.lastx = x
        self.lasty = y