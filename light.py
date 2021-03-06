"""Example using OpenGL lighting features.

Author: Christian Duncan
Course: CSC345: Computer Graphics
Term: Spring 2021

This code demonstrates how to use the lighting features of OpenGL
to render a lit scene.  Technically, these lighting features are
now deprecated in OpenGL in favor of fasterfvertex/pixel shaders 
but implementing shaders either requires cutting/pasting sample code 
or understanding all of the lighting techniques first anyway as well
as the shader language.

This demo code builds off of previous demos so the scene is similar
but it includes a floor which is illuminated by the light.
There are various types of floors that can be switched around to
see the resulting effect.
"""

# ===================
#
# THIS FILE IS FOR REFERENCE AND TESTING!!!
#
# ===================

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
from utils import *
from camera import *
import math

# These parameters describe window properties
win_width = 800
win_height = 800
win_name = b'Lights, cameras, action!'

# These parameters define the camera's lens shape and position
CAM_NEAR = 0.01
CAM_FAR = 1000.0
CAM_ANGLE = 60.0
INITIAL_EYE = Point(0, 2, 30)
INITIAL_LOOK_ANGLE = 0
camera = Camera(CAM_ANGLE, win_width/win_height, CAM_NEAR, CAM_FAR, INITIAL_EYE, INITIAL_LOOK_ANGLE)

# These parameters define simple animation properties
FPS = 60.0
DELAY = int(1000.0 / FPS + 0.5)
DEFAULT_STEP = 0.001
BULLET_SPEED = 0.1
angle_step = 0.1
angle_movement = 45
light_height = 10
light_height_dy = 0.05
LIGHT_TOP = 30
LIGHT_BOTTOM = -5
bullet_distance = 0
time = 0
brightness = 1.0

# These parameters are flags that can be turned on and off (for effect)
animate = False
fire = False
is_light_on = True
exiting = False
use_smooth = True
use_spotlight = True
use_lv = GL_FALSE
floor_option = 2

def main():
    """Start the main program running."""
    # Create the initial window.
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(win_width, win_height)
    glutInitWindowPosition(100,100)
    glutCreateWindow(win_name)

    init()

    # Setup the callback returns for display and keyboard events.
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutReshapeFunc(reshape)
    glutTimerFunc(DELAY, timer, 0)

    # Enter the main loop, displaying window and waiting for events.
    glutMainLoop()
    return

def init():
    """Perform basic OpenGL initialization."""
    global tube, ball
    tube = gluNewQuadric()
    gluQuadricDrawStyle(tube, GLU_FILL)
    ball = gluNewQuadric()
    gluQuadricDrawStyle(ball, GLU_FILL)

    # Set up lighting and depth-test
    glEnable(GL_LIGHTING)
    glEnable(GL_NORMALIZE)    # Inefficient...
    glEnable(GL_DEPTH_TEST)   # For z-buffering!

def display():
    """Display the current scene."""
    # Set the viewport to the full screen.
    glViewport(0, 0, 2*win_width, 2*win_height) # MAC USERS: Scale width and height by 2

    camera.setProjection()
    
    # Clear the Screen.
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Set the shading model we want to use.
    glShadeModel(GL_SMOOTH if use_smooth else GL_FLAT)

    # Draw and show the "Scene".
    draw_scene()
    glFlush()
    glutSwapBuffers()

def timer(alarm):
    """Set a new alarm after DELAY microsecs and animate if needed."""
    # Start alarm clock again.
    glutTimerFunc(DELAY, timer, 0)
    if exiting:
        global brightness
        brightness -= 0.05
        if brightness < 0.01:
            # Enough dimming - terminate!
            glutLeaveMainLoop()
        glutPostRedisplay()
        
    if animate:
        # Advance to the next frame.
        advance()
        glutPostRedisplay()

def advance():
    """Advance the scene one frame."""
    global angle_movement, bullet_distance, fire, time
    time += 1
    angle_movement += angle_step
    if angle_movement >= 360:
        angle_movement -= 360   # So angle doesn't get too large.
    elif angle_movement < 0:
        angle_movement += 360   # So angle doesn't get too small.

    # Move the bullet - if fired.
    if fire:
        bullet_distance += BULLET_SPEED
        if bullet_distance > CAM_FAR:
            bullet_distance = 0
            fire = False
        
def special_keys(key, x, y):
    """Process any special keys that are pressed."""
    global angle_step
    if key == GLUT_KEY_LEFT:
        angle_step += DEFAULT_STEP
    elif key == GLUT_KEY_RIGHT:
        angle_step -= DEFAULT_STEP

def keyboard(key, x, y):
    """Process any regular keys that are pressed."""
    global brightness, floor_option
    if ord(key) == 27:  # ASCII code 27 = ESC-key
        global exiting
        exiting = True
    elif key == b' ':
        global animate
        animate = not animate
    elif key == b'a':
        # Go left
        camera.turn(2)
        glutPostRedisplay()
    elif key == b'd':
        # Go right
        camera.turn(-2)
        glutPostRedisplay()
    elif key == b'w':
        # Go forward
        camera.slide(0, 0, -2)
        glutPostRedisplay()
    elif key == b's':
        # Go backward
        camera.slide(0, 0, 2)
        glutPostRedisplay()
    elif key == b'q':
        # Go up
        camera.slide(0, 1, 0)
        glutPostRedisplay()
    elif key == b'e':
        # Go down
        camera.slide(0, -1, 0)
        glutPostRedisplay()
    elif key == b'f':
        global fire
        fire = True
    elif key == b'l':
        global is_light_on
        is_light_on = not is_light_on
        glutPostRedisplay()
    elif key == b'1':
        global use_smooth
        use_smooth = not use_smooth
        glutPostRedisplay()
    elif key == b'2':
        global use_spotlight
        use_spotlight = not use_spotlight
        glutPostRedisplay()
    elif key == b'3':
        global use_lv
        use_lv = GL_FALSE if use_lv == GL_TRUE else GL_TRUE
        glutPostRedisplay()
    elif key == b'4':
        brightness = brightness * 0.9
        glutPostRedisplay()
    elif key == b'5':
        brightness = brightness / 0.9
        if brightness > 1.0:
            brightness = 1.0
        glutPostRedisplay()
    elif key == b'6':
        floor_option = floor_option+1 if floor_option < 4 else 1
        glutPostRedisplay()
    elif key == b'7':
        floor_option = floor_option-1 if floor_option > 1 else 4
        glutPostRedisplay()
    elif key == b'-':
        # Move light down
        global light_height
        light_height -= light_height_dy
        glutPostRedisplay()
    elif key == b'+':
        # Move light up
        light_height += light_height_dy
        glutPostRedisplay()

def reshape(w, h):
    """Handle window reshaping events."""
    global win_width, win_height
    win_width = w
    win_height = h
    glutPostRedisplay()  # May need to call a redraw...

def draw_scene():
    """Draws a simple scene with a few shapes."""
    # Place the camera
    camera.placeCamera()
    
    # Set up the global ambient light.  (Try commenting out.)
    amb = [ 0*brightness, 0*brightness, 0*brightness, 1.0 ]
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, amb)

    # Set up the main light (LIGHT0)... or not.
    if is_light_on:
        place_main_light()
    else:
        glDisable(GL_LIGHT0)

    # Now spin the world around the y-axis (for effect).
    glRotated(angle_movement, 0, 1, 0)
    draw_objects() 

def draw_objects():
    """Draw the objects in the scene: cylinders, spheres, and floor."""
    if floor_option == 1:
        # Draw a floor with bad lighting effects.
        draw_floor(30, 2)
    elif floor_option == 2:
        # Draw a floor with improved lighting effects.
        draw_floor(30, 30)
    elif floor_option == 3:
        # Draw a wavy floor with decent lighting.
        draw_floor(30, 30, wave)
    else:
        # Draw a nice wavy floor with proper surface normals.
        draw_floor(30, 30, wave, set_normal_wave)
    
    glPushMatrix()
    glTranslated(0, 6, 0)
    set_copper(GL_FRONT)   # Make material attributes mimic copper.
    gluCylinder(tube, 3, 3, 10, 10, 10)
    gluCylinder(tube, 3, 1, 10, 10, 10)
    glPushMatrix()
    glTranslated(0, 0, bullet_distance)
    glScaled(1, 1, 2)
    gluSphere(ball, 0.9, 10, 10)
    glPopMatrix()
    glPopMatrix()

def wave(x, z):
    """Returns a point on a 2-d "wave" trigonemtric function."""
    return math.sin(x+time*0.01)*0.25 + math.sin(z+time*0.001)*0.25

def set_normal_wave(x, z):
    """Sets the normal of a point on the aforementioned wave.

    The calculation is done using the derivatives of the wave function
    and would need to be rewritten if wave function changes.

    Keyword arguments:
    x -- The x position on the "wave"
    z -- The y position on the "wave"
    """
    glNormal3f(-0.25*math.cos(x+time*0.01), 1, 
               -0.25*math.cos(z+time*0.001))

def draw_floor(size, divisions=1, f=None, df=None):
    """Draws a floor of a given size and type.

    Keyword arguments:
    size -- Size of the floor (size x size grid, centered at origin)
    divisions -- Number of divisions (default 1)
    f -- Function to apply for the "y-height" (default None => y=0)
    df -- Procedure to set the normal based on function f (default None)
    
    A larger number of divisions great improves quality of the floor.
    If df is None then the normal is set to point directly up.
    """
    # Be sure we are talking about correct matrix.
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()

    # Make the floor mimic Pewter material.
    set_pewter(GL_FRONT_AND_BACK)   

    step = size / divisions
    if f is None:
        glNormal3f(0, 1, 0)        # Use a vertical normal.
        glBegin(GL_QUADS)
        for i in range(0, divisions):
            x = -size/2 + i*step
            for j in range(0, divisions):
                z = -size/2 + j*step
                glVertex3f(x,0,z+step)
                glVertex3f(x+step,0,z+step)
                glVertex3f(x+step,0,z)
                glVertex3f(x,0,z)
        glEnd()
    elif df is None:
        glNormal3f(0, 1, 0)        # Use a vertical normal.
        glBegin(GL_QUADS)
        for i in range(0, divisions):
            x = -size/2 + i*step
            for j in range(0, divisions):
                z = -size/2 + j*step
                glVertex3f(x,f(x,z+step),z+step)
                glVertex3f(x+step,f(x+step,z+step),z+step)
                glVertex3f(x+step,f(x+step,z),z)
                glVertex3f(x,f(x,z),z)
        glEnd()
    else:
        for i in range(0, divisions):
            glBegin(GL_QUAD_STRIP)  # QUAD_STRIPS are more efficient.
            x = -size/2 + i*step
            for j in range(0, divisions):
                z = -size/2 + j*step
                df(x+step, z)
                glVertex3f(x+step,f(x+step,z),z)
                df(x, z)
                glVertex3f(x,f(x,z),z)
            df(x+step, size/2)
            glVertex3f(x+step,f(x+step,size/2),size/2)
            df(x, size/2)
            glVertex3f(x,f(x,size/2),size/2)
            glEnd()
    glPopMatrix()

def place_main_light():
    """Set up the main light."""
    glMatrixMode(GL_MODELVIEW)
    lx = 3.0
    ly = light_height
    lz = 1.0
    light_position = [ lx, ly, lz, 1.0 ]
    light_ambient = [ 1*brightness, 1*brightness, 1*brightness, 1.0 ]
    light_diffuse = [ 1*brightness, 1*brightness, 1*brightness, 1.0 ]
    light_specular = [ 1*brightness, 1*brightness, 1*brightness, 1.0 ]
    light_direction = [ 1.0, -1.0, 1.0, 0.0 ]  # Light points down

    # For Light 0, set position, ambient, diffuse, and specular values
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    # Constant attenuation (for distance, etc.)
    # Only works for fixed light locations!  Otherwise disabled
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.0)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.0)
    
    # Create a spotlight effect (none at the moment)
    if use_spotlight:
        glLightf(GL_LIGHT0, GL_SPOT_CUTOFF,45.0)
        glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 0.0)
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, light_direction)
    else:
        glLightf(GL_LIGHT0, GL_SPOT_CUTOFF,180.0)
        glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 0.0)
    
    glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, use_lv)
    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
    #  Try GL_TRUE - but then watch what happens when light is low
    
    glEnable(GL_LIGHT0)

    # This part draws a SELF-COLORED sphere (in spot where light is!)
    glPushMatrix()
    glTranslatef(lx,ly,lz)
    glDisable(GL_LIGHTING)
    glColor3f(0, 0, brightness)
    glutSolidSphere(0.5, 20, 20)
    glEnable(GL_LIGHTING)
    glPopMatrix()

def set_copper(face):
    """Set the material properties of the given face to "copper"-esque.

    Keyword arguments:
    face -- which face (GL_FRONT, GL_BACK, or GL_FRONT_AND_BACK)
    """
    ambient = [ 0.19125, 0.0735, 0.0225, 1.0 ]
    diffuse = [ 0.7038, 0.27048, 0.0828, 1.0 ]
    specular = [ 0.256777, 0.137622, 0.086014, 1.0 ]
    shininess = 128.0
    glMaterialfv(face, GL_AMBIENT, ambient);
    glMaterialfv(face, GL_DIFFUSE, diffuse);
    glMaterialfv(face, GL_SPECULAR, specular);
    glMaterialf(face, GL_SHININESS, shininess);
    
def set_pewter(face):
    """Set the material properties of the given face to "pewter"-esque.

    Keyword arguments:
    face -- which face (GL_FRONT, GL_BACK, or GL_FRONT_AND_BACK)
    """
    ambient = [ 0.10588, 0.058824, 0.113725, 1.0 ]
    diffuse = [ 0.427451, 0.470588, 0.541176, 1.0 ]
    specular = [ 0.3333, 0.3333, 0.521569, 1.0 ]
    shininess = 9.84615
    glMaterialfv(face, GL_AMBIENT, ambient);
    glMaterialfv(face, GL_DIFFUSE, diffuse);
    glMaterialfv(face, GL_SPECULAR, specular);
    glMaterialf(face, GL_SHININESS, shininess);

if __name__ == '__main__': main()
