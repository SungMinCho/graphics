#include <math.h>   // smallpt, a Path Tracer by Kevin Beason, 2009
#include <stdlib.h> // Make : g++ -O3 -fopenmp explicit.cpp -o explicit
#include <stdio.h>  //        Remove "-fopenmp" for g++ version < 4.2
struct Vec {        // Usage: time ./explicit 16 && xv image.ppm
  double x, y, z;                  // position, also color (r,g,b)
  Vec(double x_=0, double y_=0, double z_=0){ x=x_; y=y_; z=z_; }
  Vec operator+(const Vec &b) const { return Vec(x+b.x,y+b.y,z+b.z); }
  Vec operator-(const Vec &b) const { return Vec(x-b.x,y-b.y,z-b.z); }
  Vec operator*(double b) const { return Vec(x*b,y*b,z*b); }
  Vec mult(const Vec &b) const { return Vec(x*b.x,y*b.y,z*b.z); }
  Vec& norm(){ return *this = *this * (1/sqrt(x*x+y*y+z*z)); }
  double dot(const Vec &b) const { return x*b.x+y*b.y+z*b.z; } // cross:
  Vec operator%(Vec&b) const {return Vec(y*b.z-z*b.y,z*b.x-x*b.z,x*b.y-y*b.x);}
};
struct Ray { Vec o, d; Ray(Vec o_, Vec d_) : o(o_), d(d_) {} };
enum Refl_t { DIFF, SPEC, REFR };  // material types, used in radiance()
class Object {
public:
  double rad;
  Vec p, e, c;
  Refl_t refl;
  Object(double rad_, Vec p_, Vec e_, Vec c_, Refl_t refl_):
    rad(rad_), p(p_), e(e_), c(c_), refl(refl_) {}
  virtual double intersect(const Ray &r) = 0;
  virtual Vec normal(Vec x) = 0;
};
class Sphere : public Object {
public:
  //double rad;       // radius
  //Vec p, e, c;      // position, emission, color
  //Refl_t refl;      // reflection type (DIFFuse, SPECular, REFRactive)
  Sphere(double rad_, Vec p_, Vec e_, Vec c_, Refl_t refl_):
    Object(rad_, p_, e_, c_, refl_) {}
  virtual double intersect(const Ray &r) { // returns distance, 0 if nohit
    Vec op = p-r.o; // Solve t^2*d.d + 2*t*(o-p).d + (o-p).(o-p)-R^2 = 0
    double t, eps=1e-4, b=op.dot(r.d), det=b*b-op.dot(op)+rad*rad;
    if (det<0) return 0; else det=sqrt(det);
    return (t=b-det)>eps ? t : ((t=b+det)>eps ? t : 0);
  }
  virtual Vec normal(Vec x) {
    return (x-p).norm();
  }
};
class Triangle : public Object {
public:
  Vec n, center;
  Vec p1, p2, p3, e1, e2;
  Triangle(Vec p1_, Vec p2_, Vec p3_, Vec e_, Vec c_, Refl_t refl_):
    p1(p1_), p2(p2_), p3(p3_), Object(0, Vec(), e_, c_, refl_) {
      e1 = p2 - p1;
      e2 = p3 - p1;
      n = e1%e2;
      n.norm();
      //n = n * -1;
      center = Vec();
      center = center + p1;
      center = center + p2;
      center = center + p3;
      center = center * (0.333333333);
      //center = center + n;
      p = center;
      Vec t = center - p1;
      rad = t.dot(t);
    }

  virtual double intersect(const Ray &r) {
    //Vec e1, e2;  //Edge1, Edge2
    Vec P, Q, T;
    double det, inv_det, u, v;
    double t;
    double EPSILON = 1e-4;

    //Find vectors for two edges sharing V1
    //e1 = p2 - p1;
    //e2 = p3 - p1;
    //Begin calculating determinant - also used to calculate u parameter
    P = r.d % e2;
    //if determinant is near zero, ray lies in plane of triangle
    det = e1.dot(P);
    //NOT CULLING
    if(det > -EPSILON && det < EPSILON) return 0;
    inv_det = 1.0 / det;

    //calculate distance from V1 to ray origin
    T = r.o - p1;

    //Calculate u parameter and test bound
    u = T.dot(P) * inv_det;
    //The intersection lies outside of the triangle
    if(u < 0.f || u > 1.f) return 0;

    //Prepare to test v parameter
    Q = T % e1;

    //Calculate V parameter and test bound
    v = r.d.dot(Q) * inv_det;
    //The intersection lies outside of the triangle
    if(v < 0.f || u + v  > 1.f) return 0;

    t = e2.dot(Q) * inv_det;

    if(t > EPSILON) { //ray intersection
      //*out = t;
      return t;
    }

    // No hit, no win
    return 0;
  }

  virtual Vec normal(Vec x) {
    return n;
  }
};
Object* objects[] = {//Scene: radius, position, emission, color, material
  new Sphere(1e5, Vec( 1e5-9,40.8,81.6), Vec(),Vec(.75,.25,.25),DIFF),//Left
  new Sphere(1e5, Vec(-1e5+109,40.8,81.6),Vec(),Vec(.25,.25,.75),DIFF),//Rght
  new Sphere(1e5, Vec(50,40.8, 1e5),     Vec(),Vec(.75,.75,.75),DIFF),//Back
  new Sphere(1e5, Vec(50,40.8,-1e5+170), Vec(),Vec(.75,.75,.75),DIFF),//Frnt
  new Sphere(1e5, Vec(50, 1e5-10, 81.6),    Vec(),Vec(.75,.75,.75),DIFF),//Botm
  new Sphere(1e5, Vec(50,-1e5+91.6,81.6),Vec(),Vec(.75,.75,.75),DIFF),//Top
  new Sphere(16.5,Vec(27,16.5-10,47),       Vec(),Vec(1,1,1)*.999, SPEC),//Mirr
  new Sphere(10,Vec(27,50,50),       Vec(),Vec(0.2,0.6,0.2)*.999, DIFF),//Above
  new Sphere(16.5,Vec(73,16.5-10,78),       Vec(),Vec(1,1,1)*.999, REFR),//Glas
  new Sphere(1.5, Vec(50,81.6-6.5,81.6),Vec(4,4,4)*100,  Vec(), DIFF),//Lite
  //new Triangle(Vec(50, 16.5, 60), Vec(80, 16.5+40, 47), Vec(40, 16.5+25, 25), Vec(), Vec(1,1,1)*.999, SPEC),

  new Triangle(Vec(7, 70, 60), Vec(7, 50, 50), Vec(27, 70, 40), Vec(), Vec(1,1,1)*.999, SPEC),
  new Triangle(Vec(7, 50, 50), Vec(27, 50, 30), Vec(27, 70, 40), Vec(), Vec(1,1,1)*.999, SPEC),
  new Triangle(Vec(27, 70, 40), Vec(27, 50, 30), Vec(47, 70, 60), Vec(), Vec(1,1,1)*.999, SPEC),
  new Triangle(Vec(27, 50, 30), Vec(47, 50, 50), Vec(47, 70, 60), Vec(), Vec(1,1,1)*.999, SPEC),
};
//int numObjects = sizeof(objects)/sizeof(Object);
int numObjects = 14;
inline double clamp(double x){ return x<0 ? 0 : x>1 ? 1 : x; }
inline int toInt(double x){ return int(pow(clamp(x),1/2.2)*255+.5); }
inline bool intersect(const Ray &r, double &t, int &id){
  double d, inf=t=1e20;
  for(int i=numObjects;i--;) if((d=objects[i]->intersect(r))&&d<t){t=d;id=i;}
  return t<inf;
}
Vec radiance(const Ray &r, int depth, unsigned short *Xi,int E=1){
  double t;                               // distance to intersection
  int id=0;                               // id of intersected object
  if (!intersect(r, t, id)) return Vec(); // if miss, return black
  Object* obj = objects[id];        // the hit object
  Vec x=r.o+r.d*t, n=obj->normal(x), nl=n.dot(r.d)<0?n:n*-1, f=obj->c;
  double p = f.x>f.y && f.x>f.z ? f.x : f.y>f.z ? f.y : f.z; // max refl
  if (++depth>5||!p) if (erand48(Xi)<p) f=f*(1/p); else return obj->e*E;
  if (obj->refl == DIFF){                  // Ideal DIFFUSE reflection
    double r1=2*M_PI*erand48(Xi), r2=erand48(Xi), r2s=sqrt(r2);
    Vec w=nl, u=((fabs(w.x)>.1?Vec(0,1):Vec(1))%w).norm(), v=w%u;
    Vec d = (u*cos(r1)*r2s + v*sin(r1)*r2s + w*sqrt(1-r2)).norm();

    // Loop over any lights
    Vec e;
    for (int i=0; i<numObjects; i++){
      Object* s = objects[i];
      if (s->e.x<=0 && s->e.y<=0 && s->e.z<=0) continue; // skip non-lights
      
      Vec sw=s->p-x, su=((fabs(sw.x)>.1?Vec(0,1):Vec(1))%sw).norm(), sv=sw%su;
      double cos_a_max = sqrt(1-s->rad*s->rad/(x-s->p).dot(x-s->p));
      double eps1 = erand48(Xi), eps2 = erand48(Xi);
      double cos_a = 1-eps1+eps1*cos_a_max;
      double sin_a = sqrt(1-cos_a*cos_a);
      double phi = 2*M_PI*eps2;
      Vec l = su*cos(phi)*sin_a + sv*sin(phi)*sin_a + sw*cos_a;
      l.norm();
      if (intersect(Ray(x,l), t, id) && id==i){  // shadow ray
        double omega = 2*M_PI*(1-cos_a_max);
        e = e + f.mult(s->e*l.dot(nl)*omega)*M_1_PI;  // 1/pi for brdf
      }
    }
    
    return obj->e*E+e+f.mult(radiance(Ray(x,d),depth,Xi,0));
  } else if (obj->refl == SPEC)              // Ideal SPECULAR reflection
    return obj->e + f.mult(radiance(Ray(x,r.d-n*2*n.dot(r.d)),depth,Xi));
  Ray reflRay(x, r.d-n*2*n.dot(r.d));     // Ideal dielectric REFRACTION
  bool into = n.dot(nl)>0;                // Ray from outside going in?
  double nc=1, nt=1.5, nnt=into?nc/nt:nt/nc, ddn=r.d.dot(nl), cos2t;
  if ((cos2t=1-nnt*nnt*(1-ddn*ddn))<0)    // Total internal reflection
    return obj->e + f.mult(radiance(reflRay,depth,Xi));
  Vec tdir = (r.d*nnt - n*((into?1:-1)*(ddn*nnt+sqrt(cos2t)))).norm();
  double a=nt-nc, b=nt+nc, R0=a*a/(b*b), c = 1-(into?-ddn:tdir.dot(n));
  double Re=R0+(1-R0)*c*c*c*c*c,Tr=1-Re,P=.25+.5*Re,RP=Re/P,TP=Tr/(1-P);
  return obj->e + f.mult(depth>2 ? (erand48(Xi)<P ?   // Russian roulette
    radiance(reflRay,depth,Xi)*RP:radiance(Ray(x,tdir),depth,Xi)*TP) :
    radiance(reflRay,depth,Xi)*Re+radiance(Ray(x,tdir),depth,Xi)*Tr);
}
int main(int argc, char *argv[]){
  int w=1024, h=768, samps = argc==2 ? atoi(argv[1])/4 : 1; // # samples
  Ray cam(Vec(50,52,295.6), Vec(0,-0.042612,-1).norm()); // cam pos, dir
  Vec cx=Vec(w*.5135/h), cy=(cx%cam.d).norm()*.5135, r, *c=new Vec[w*h];
#pragma omp parallel for schedule(dynamic, 1) private(r)       // OpenMP
  for (int y=0; y<h; y++){                       // Loop over image rows
    fprintf(stderr,"\rRendering (%d spp) %5.2f%%",samps*4,100.*y/(h-1));
    for (unsigned short x=0, Xi[3]={0,0,y*y*y}; x<w; x++)   // Loop cols
      for (int sy=0, i=(h-y-1)*w+x; sy<2; sy++)     // 2x2 subpixel rows
        for (int sx=0; sx<2; sx++, r=Vec()){        // 2x2 subpixel cols
          for (int s=0; s<samps; s++){
            double r1=2*erand48(Xi), dx=r1<1 ? sqrt(r1)-1: 1-sqrt(2-r1);
            double r2=2*erand48(Xi), dy=r2<1 ? sqrt(r2)-1: 1-sqrt(2-r2);
            Vec d = cx*( ( (sx+.5 + dx)/2 + x)/w - .5) +
                    cy*( ( (sy+.5 + dy)/2 + y)/h - .5) + cam.d;
            r = r + radiance(Ray(cam.o+d*140,d.norm()),0,Xi)*(1./samps);
          } // Camera rays are pushed ^^^^^ forward to start in interior
          c[i] = c[i] + Vec(clamp(r.x),clamp(r.y),clamp(r.z))*.25;
        }
  }
  FILE *f = fopen("image.ppm", "w");         // Write image to PPM file.
  fprintf(f, "P3\n%d %d\n%d\n", w, h, 255);
  for (int i=0; i<w*h; i++)
    fprintf(f,"%d %d %d ", toInt(c[i].x), toInt(c[i].y), toInt(c[i].z));
}