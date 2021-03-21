#==============================
# Christian Duncan
# CSC345: Computer Graphics
#   Spring 2021
#
# camera.py module
# Description:
#   Defines a simple camera class for navigation
#==============================
import math
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from utils import *

class Camera:
    """A simple 3D Camera System"""

    def __init__(self, camAngle=45, aspRatio=1, near=0.1, far=1000, eye=Point(0,0,0), lookAngle=0):
        """A constructor for Camera class using initial default values.
           eye is a Point
           lookAngle is the angle that camera is looking in measured in degrees
        """
        self.camAngle = camAngle
        self.aspRatio = aspRatio
        self.near = near
        self.far = far
        self.eye = eye
        self.lookAngle = lookAngle

    def __str__(self):
        """Basic string representation of this Camera"""
        return "Camera Eye at %s with angle (%f)"%(self.eye, self.lookAngle)

    def setProjection(self):
        glMatrixMode(GL_PROJECTION);
        glLoadIdentity();
        # Set view to Perspective Proj. (angle, aspect ratio, near/far planes)
        gluPerspective(self.camAngle, self.aspRatio, self.near, self.far)
    
    def placeCamera(self):
        glMatrixMode(GL_MODELVIEW);
        glLoadIdentity();

        # Compute the look at point based on the turn angle
        rad = math.radians(self.lookAngle)
        lookX = self.eye.x - math.sin(rad)
        lookY = self.eye.y
        lookZ = self.eye.z - math.cos(rad)

        # Place the camera
        gluLookAt(self.eye.x, self.eye.y, self.eye.z,  # Camera's origin
                  lookX, lookY, lookZ,                 # Camera's look at point
                  0, 1, 0)                             # Camera is always oriented vertically
        
    def slide(self, du, dv, dn):
        # This is not complete!  It does not move along the u-axis (x-axis)!
        rad = math.radians(self.lookAngle)
        lookDX = math.sin(rad)
        lookDZ = math.cos(rad)
        
        self.eye.x += dn*lookDX
        self.eye.y += dv
        self.eye.z += dn*lookDZ
    
    def turn(self, angle):
        """ Turn the camera by the given angle"""
        self.lookAngle += angle
        if self.lookAngle < 0: self.lookAngle += 360  # Just to wrap around
        elif self.lookAngle >= 360: self.lookAngle -= 360  # Just to wrap around
        
