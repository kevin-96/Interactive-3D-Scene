#==============================
# Christian Duncan
# CSC345: Computer Graphics
#   Spring 2021
#
# Modified By: Phillip Nam
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

    # Global Variables
    lookX = 0
    lookY = 0
    lookZ = 0

    def __init__(self, camAngle=45, aspRatio=1, near=0.1, far=1000, eye=Point(0,0,0), lookAngle=0, tiltAngle=0):
        """A constructor for Camera class using initial default values.
           eye is a Point
           lookAngle is the horizontal angle that camera is looking in measured in degrees
           tiltAngle is the vertical angle that camera is looking in measured in degrees
        """
        self.camAngle = camAngle
        self.aspRatio = aspRatio
        self.near = near
        self.far = far
        self.eye = eye
        # self.startPos = eye
        self.lookAngle = lookAngle # For Yaw
        self.tiltAngle = tiltAngle # For Pitch

    def __str__(self):
        """Basic string representation of this Camera"""
        return "Camera Eye at %s with turn angle (%f) and tilt angle (%f)"%(self.eye, self.lookAngle, self.tiltAngle)

    def setProjection(self):
        glMatrixMode(GL_PROJECTION);
        glLoadIdentity();
        # Set view to Perspective Proj. (angle, aspect ratio, near/far planes)
        gluPerspective(self.camAngle, self.aspRatio, self.near, self.far)
    
    def placeCamera(self):
        glMatrixMode(GL_MODELVIEW);
        glLoadIdentity();

        global lookX, lookY, lookZ

        # Compute the look at point based on the turn (Yaw) and tilt (Pitch) angle
        radTurn = math.radians(self.lookAngle)
        radTilt = math.radians(self.tiltAngle)

        lookX = self.eye.x - math.sin(radTurn)
        lookY = self.eye.y + math.sin(radTilt)
        lookZ = self.eye.z - math.cos(radTurn)

        # Place the camera
        gluLookAt(self.eye.x, self.eye.y, self.eye.z,  # Camera's origin
                  lookX, lookY, lookZ,                 # Camera's look at point
                  0, 1, 0)                             # Camera is always oriented vertically

    def setPosition(self, point):
        # glMatrixMode(GL_MODELVIEW);
        # glLoadIdentity();
        global lookX, lookY, lookZ

        self.eye.x = point.x
        self.eye.y = point.y
        self.eye.z = point.z

        gluLookAt(self.eye.x, self.eye.y, self.eye.z,   # Camera's starting position
                  lookX, lookY, lookZ,                  # Camera's look at point (remains same)
                  0, 1, 0)                              # Camera is always oriented vertically

    def slide(self, du, dv, dn):
        rad = math.radians(self.lookAngle)
        lookDX = math.sin(rad)
        lookDZ = math.cos(rad)
        
        self.eye.x += dn*lookDX + du*lookDZ
        self.eye.y += dv
        self.eye.z += dn*lookDZ - du*lookDX
    
    def turn(self, angle):
        """ Turn the camera by the given angle (Yaw)"""
        self.lookAngle += angle
        if self.lookAngle < 0: self.lookAngle += 360  # Just to wrap around
        elif self.lookAngle >= 360: self.lookAngle -= 360  # Just to wrap around

    def tilt(self, angle):
        """ Tilt the camera by the given angle (Pitch)"""
        self.tiltAngle += angle
        tiltBound = 90 # Tilt restriction (degrees)
        if self.tiltAngle >= tiltBound: self.tiltAngle = tiltBound  # Tilt angle upward limit is 90 degrees
        elif self.tiltAngle <= -tiltBound: self.tiltAngle = -tiltBound  # Tilt angle downward limit is -90 degrees

    def levelTilt(self):
        """ Set camera tilt (Pitch) to 0 (Look straight ahead)"""
        self.tiltAngle = 0