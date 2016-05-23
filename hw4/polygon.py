from quaternion import *

class Polygon:
  def __init__(self, points, R, G, B, A):
    # points should all be on the same plane
    self.points = points
    self.normal = Vector.cross(points[1]-points[0], points[2]-points[0])
    self.R = R
    self.G = G
    self.B = B
    self.A = A

  def draw(self):
    glColor4f(self.R, self.G, self.B, self.A)
    glBegin(GL_POLYGON)
    for p in self.points:
      glVertex3f(p.x, p.y, p.z)
    glEnd()

  def point_side(self, p):
    p0 = self.points[0]
    p1 = self.points[1]

    v0 = p1 - p0
    v1 = p - p0

    c = Vector.cross(v0, v1)
    if c < 0:
      return -1
    elif c > 0:
      return 1
    else:
      return 0

  def cut_polygon(self, polygon):
    #return (list of left (<=) of self, list of right (>) of self)
    pass

  def divide_polygon(self, polygon):
    # return polygon pair of (list of left (<=) of self, list of right (>) of self)
    # left and right is just negativeness and positiveness of cross result
    s = self.point_side(polygon.points[0])
    for p in polygon.points[1:]:
      ss = self.point_side(p)
      if ss != s:
        if ss * s != 0: #really on the other side
          return self.cut_polygon(polygon)
        else:
          if s == 0: # if it's 1 0 1 1 0, 1 is the representative (if we keep s as 0 then we might mistake it for left (<= 0))
            s = ss

    if s <= 0:
      return ([polygon], [])
    else:
      return ([], [polygon])

  def ray_intersection(self, p0, p1):
    v0 = self.points[0]
    n = self.normal
    r = (Vector.dot(n, (v0 - p0))) / (Vector.dot(n, (p1 - p0)))
    return (p0 + (r * (p1 - p0)))

class Triangle(Polygon):
  def cut_polygon(self, polygon):
    assert(len(polygon.points) == 3) # only deal with triangles
    left = []
    same = []
    right = []
    for p in polygon.points:
      s = self.point_side(p)
      if s < 0:
        left.append(p)
      elif s > 0:
        right.append(p)
      else:
        same.append(p)

    assert(len(left) > 0 and len(right) > 0) # at least one on each side (only reason we cut)

    # find the two intersecting points.
    # should be two. if <= 1, then we don't cut in the first place


    if len(same) == 1 : # len(same) is at most one because of the condition above
      i0 = same[0]
      i1 = self.ray_intersection(right[0], left[0])

      leftTriangle = Triangle([left[0], i0, i1], self.R, self.G, self.B, self.A)
      rightTriangle = Triangle([right[0], i0, i1], self.R, self.G, self.B, self.A)
      return ([leftTriangle], [rightTriangle])
    elif len(left) == 2: # two on left side
      i0 = self.ray_intersection(right[0], left[0])
      i1 = self.ray_intersection(right[0], left[1])

      # find diagonal
      v0 = i1 - left[0]
      v1 = i0 - left[0]
      v2 = left[1] - left[0]
      if Vector.cross(v0, v1) * Vector.cross(v0, v2) < 0:
        diagonal = i1
        other = i0
      else:
        diagonal = i0
        other = i1
      leftTriangle1 = Triangle([left[0], other, diagonal], self.R, self.G, self.B, self.A)
      leftTriangle2 = Triangle([left[0], diagonal, left[1]], self.R, self.G, self.B, self.A)
      rightTriangle = Triangle([right[0], i0, i1], self.R, self.G, self.B, self.A)
      return ([leftTriangle1, leftTriangle2], [rightTriangle])
    else: # two on right side
      i0 = self.ray_intersection(left[0], right[0])
      i1 = self.ray_intersection(left[1], right[0])

      # find diagonal
      v0 = i1 - right[0]
      v1 = i0 - right[0]
      v2 = right[1] - right[0]
      if Vector.cross(v0, v1) * Vector.cross(v0, v2) < 0:
        diagonal = i1
        other = i0
      else:
        diagonal = i0
        other = i1
      rightTriangle1 = Triangle([right[0], other, diagonal], self.R, self.G, self.B, self.A)
      rightTriangle2 = Triangle([right[0], diagonal, right[1]], self.R, self.G, self.B, self.A)
      leftTriangle = Triangle([left[0], i0, i1], self.R, self.G, self.B, self.A)
      return ([leftTriangle], [rightTriangle1, rightTriangle2])


class BSP:
  def __init__(self, polygons):
    assert(len(polygons) > 0)
    if(len(polygons) == 1):
      self.isLeaf = True
      self.node = polygons[0]
    else:
      self.isLeaf = False
      left = []
      right = []
      n = polygons[0]
      self.node = n
      for p in polygons[1:]:
        d = n.divide_polygon(p)
        for l in d[0]:
          left.append(l)
        for r in d[1]:
          right.append(r)

      self.leftTree = BSP(left)
      self.rightTree = BSP(right)

  def draw(self, viewpoint):
    if self.isLeaf:
      self.node.draw()
      return

    s = self.node.point_side(viewpoint)
    if s < 0:
      self.rightTree.draw(viewpoint)
      self.node.draw()
      self.leftTree.draw(viewpoint)
    elif s > 0:
      self.leftTree.draw(viewpoint)
      self.node.draw()
      self.rightTree.draw(viewpoint)
    else:
      # i guess order doesn't matter in this case...?
      self.leftTree.draw(viewpoint)
      self.rightTree.draw(viewpoint)