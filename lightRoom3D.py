# ==============================
#
# ASSIGNMENT 3: Interactive 3D Scene
#
# Authors: Phillip Nam, Kevin Sangurima, Ryan Clark
# Course: CSC345 - Computer Graphics
# Term: Spring 2021
#
# This program showcases the use of lighting in OpenGL.
# The user is allowed to navigate through a room which features various
# textured objects and multiple light sources.
# The main purpose of the program is to observe the interaction between
# light sources in an environment and the objects within it.
#
# ==============================

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from PIL import Image
import sys
from utils import *
from camera import *
import math

# These parameters describe window properties
win_width = 800
win_height = 800
win_name = b'Mi Casa Es Su Casa :) Bienvenidos'

# These parameters define the camera's lens shape and position
CAM_NEAR = 0.01
CAM_FAR = 1000.0
CAM_ANGLE = 60.0
INITIAL_EYE = Point(12, 7, 13)
START_EYE = Point(12, 7, 13) # Used to reset starting position of camera (Not in constructor)
INITIAL_LOOK_ANGLE = 45 # Initally, look to the left
INITIAL_TILT_ANGLE = 0 # Initially, look straight ahead
camera = Camera(CAM_ANGLE, win_width/win_height, CAM_NEAR, CAM_FAR, INITIAL_EYE, INITIAL_LOOK_ANGLE, INITIAL_TILT_ANGLE)

# These parameters define simple animation properties
FPS = 60.0
DELAY = int(1000.0 / FPS + 0.5)
DEFAULT_STEP = 0.001
angle_step = 0.1
angle_movement = 45
rgb_light_height = 15
LIGHT_TOP = 30
LIGHT_BOTTOM = -5
brightness = 1.0 # Default spotlight brightness
deskBrightness= 0.75 # Desk lamp (spotlight)
redBrightness = 1.0 # Red spotlight
blueBrightness = 1.0 # Blue spotlight
greenBrightness = 1.0 # Green spotlight
flashBrightness = 1.0 # Flashlight spotlight

# Object animation variables
diceAngle = 0 # Dice rotation (about y-axis). Never resets.
diceAngleD = 10 # Amount the dice rotates per frame
diceAngleTotal = 0 # Keeps track of total rotation amount on the dice. Will reset at end of animation
diceAngleLimit = 1000 # How much the dice can rotate at a time before the dice animation stops.
copperBallAngle = 0 # Ball rotation angle (about y-axis). Initially 0.
copperBallAngleD = 5 # Amount the copper ball rotates per frame
silverBallAngle = 0 # Ball rotation angle (about y-axis). Initially 0.
silverBallAngleD = 8 # Amount the silver ball rotates per frame

# Checkerboard dimensions (texture dimensions are powers of 2)
NROWS = 64
NCOLS = 64

# Global variables for the room
ROOM_LENGTH = 30
ROOM_WIDTH = 30
ROOM_HEIGHT = 17

# Global variables for camera boundaries
BOUND_X_MAX = 14.9
BOUND_X_MIN = -14.9
BOUND_Y_MAX = 16.9
BOUND_Y_MIN = 0.1
BOUND_Z_MAX = 14.9
BOUND_Z_MIN = -14.9

# These parameters are flags that can be turned on and off (for effect)
animateCopperBall = False
animateSilverBall = False
animateDice = False
is_light_on = False
use_spotlight = False
is_desk_spotlight_on = True
is_red_spotlight_on = True
is_blue_spotlight_on = True
is_green_spotlight_on = True
is_flash_spotlight_on = True
is_textured_picture_on = False
exiting = False
use_smooth = True
use_lv = GL_FALSE

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
    global tube, ball, cube, brickTextureName, ceilingTextureName, woodTextureName, checkerboardTextureName, secretPictureTextureName, die1TextureName, die2TextureName, die3TextureName, die4TextureName, die5TextureName, die6TextureName
    tube = gluNewQuadric()
    gluQuadricDrawStyle(tube, GLU_FILL)
    ball = gluNewQuadric()
    gluQuadricDrawStyle(ball, GLU_FILL)
    cube = gluNewQuadric()
    gluQuadricDrawStyle(cube, GLU_FILL)

    # Generate or load the textures into memory
    generateCheckerBoardTexture()
    brickTextureName = loadImageTexture("textures/brickWall.jpg")
    ceilingTextureName = loadImageTexture("textures/ceiling.jpg")
    woodTextureName = loadImageTexture("textures/wood2-crop.jpg")
    checkerboardTextureName = loadImageTexture("textures/checkerboard.png")
    secretPictureTextureName = loadImageTexture("textures/yes.jpg")
    die1TextureName = loadImageTexture("textures/dice/face1.jpg")
    die2TextureName = loadImageTexture("textures/dice/face2.jpg")
    die3TextureName = loadImageTexture("textures/dice/face3.jpg")
    die4TextureName = loadImageTexture("textures/dice/face4.jpg")
    die5TextureName = loadImageTexture("textures/dice/face5.jpg")
    die6TextureName = loadImageTexture("textures/dice/face6.jpg")
  
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
        
    if animateCopperBall:
        # Advance to the next frame.
        advanceCopperBall()
        glutPostRedisplay()

    if animateSilverBall:
        # Advance to the next frame.
        advanceSilverBall()
        glutPostRedisplay()

    if animateDice:
        # Advance to the next frame.
        advanceDice()
        glutPostRedisplay()

# Animations for the ball and dice objects in the scene
def advanceCopperBall():
    """Advance the scene one frame."""
    global copperBallAngle, copperBallAngleD
    copperBallAngle += copperBallAngleD

def advanceSilverBall():
    """Advance the scene one frame."""
    global silverBallAngle, silverBallAngleD
    silverBallAngle += silverBallAngleD

def advanceDice():
    """Advance the scene one frame."""
    global diceAngle, diceAngleD, diceAngleTotal, diceAngleLimit, animateDice
    if (diceAngleTotal >= diceAngleLimit):
        # When angle rotation limit is met, stop the animation and reset diceAngleTotal
        # print("Dice animation stopped!") # Debug
        diceAngleTotal = 0 # Reset at the end of animation
        animateDice = False # Stops the dice animation from running
    else:
        # Else, let the dice animate
        diceAngle += diceAngleD
        diceAngleTotal += diceAngleD


# Check if the camera meets the room's boundaries
def checkBounds():
    if camera.eye.x >= BOUND_X_MAX:
        camera.eye.x = BOUND_X_MAX
    elif camera.eye.x <= BOUND_X_MIN:
        camera.eye.x = BOUND_X_MIN
    if camera.eye.y >= BOUND_Y_MAX:
        camera.eye.y = BOUND_Y_MAX
    elif camera.eye.y <= BOUND_Y_MIN:
        camera.eye.y = BOUND_Y_MIN
    if camera.eye.z >= BOUND_Z_MAX:
        camera.eye.z = BOUND_Z_MAX
    elif camera.eye.z <= BOUND_Z_MIN:
        camera.eye.z = BOUND_Z_MIN

def texturedPictureCheck():
    if (not is_red_spotlight_on and not is_green_spotlight_on and not is_blue_spotlight_on and not is_desk_spotlight_on and is_flash_spotlight_on):
        is_textured_picture_on = True
        draw_Textured_Picture()
    else:
        is_textured_picture_on = False
        
def special_keys(key, x, y):
    """Process any special keys that are pressed."""
    global angle_step
    if key == GLUT_KEY_LEFT:
        angle_step += DEFAULT_STEP
    elif key == GLUT_KEY_RIGHT:
        angle_step -= DEFAULT_STEP

def keyboard(key, x, y):
    """Process any regular keys that are pressed."""
    global brightness, redBrightness, greenBrightness, blueBrightness, deskBrightness, animateDice
    if ord(key) == 27:  # ASCII code 27 = ESC-key
        global exiting
        exiting = True
    # Animation Controls
    elif key == b'j':
        # Copper ball rolls in a circle
        global animateCopperBall
        animateCopperBall = not animateCopperBall
    elif key == b'k':
        # Silver ball rolls in a circle
        global animateSilverBall
        animateSilverBall = not animateSilverBall
    elif (key == b'l') and (animateDice == False):
        # Pair of dice spin in place (and eventually stop)
        animateDice = not animateDice
    # Camera Controls
    elif key == b'w':
        # Move forward
        camera.slide(0, 0, -2)
        checkBounds() # Check if camera hits bounds
        # print(INITIAL_EYE) # Print camera's position (DEBUGGING)
        glutPostRedisplay()
    elif key == b's':
        # Move backward
        camera.slide(0, 0, 2)
        checkBounds() # Check if camera hits bounds
        glutPostRedisplay()
    elif key == b'a':
        # Move left
        camera.slide(-2, 0, 0)
        checkBounds() # Check if camera hits bounds
        glutPostRedisplay()
    elif key == b'd':
        # Move right
        camera.slide(2, 0, 0)
        checkBounds() # Check if camera hits bounds
        glutPostRedisplay()
    elif key == b'q':
        # Turn camera left
        camera.turn(3)
        glutPostRedisplay()
    elif key == b'e':
        # Turn camera right
        camera.turn(-3)
        glutPostRedisplay()
    elif key == b'r':
        # Turn camera 180 degrees
        camera.turn(180)
        glutPostRedisplay()
    elif key == b'z':
        # Tilt camera down
        camera.tilt(-3)
        glutPostRedisplay()
    elif key == b'c':
        # Tilt camera up
        camera.tilt(3)
        glutPostRedisplay()
    elif key == b'x':
        # Level gaze (straight ahead)
        camera.levelTilt()
        glutPostRedisplay()
    elif key == b't':
        # Set camera back to starting position
        # print(INITIAL_EYE) # DEBUGGING
        camera.setPosition(START_EYE)
        glutPostRedisplay()
    elif key == b'h':
        # Print help message (console)
        file = open("help.txt", "r")
        print(file.read())
    elif key == b'-':
        # Go down (DEBUGGING)
        camera.slide(0, -0.8, 0)
        checkBounds() # Check if camera hits bounds
        glutPostRedisplay()
    elif key == b'+':
        # Go up (DEBUGGING)
        camera.slide(0, 0.8, 0)
        checkBounds() # Check if camera hits bounds
        glutPostRedisplay()

    # Light Controls
    elif key == b'0':
        # Toggle desk lamp light source
        global is_desk_spotlight_on
        if is_desk_spotlight_on == True:
            is_desk_spotlight_on = False
            deskBrightness = 0.0
            glutPostRedisplay()
        elif is_desk_spotlight_on == False:
            deskBrightness = 1.0
            is_desk_spotlight_on = True
            glutPostRedisplay()
        texturedPictureCheck()
    elif key == b'1':
        # Toggle red light source
        global is_red_spotlight_on
        if is_red_spotlight_on == True:
            is_red_spotlight_on = False
            redBrightness = 0.0
            glutPostRedisplay()
        elif is_red_spotlight_on == False:
            redBrightness = 1.0
            is_red_spotlight_on = True
            glutPostRedisplay()
        texturedPictureCheck()
    elif key == b'2':
        # Toggle green light source
        global is_green_spotlight_on
        if is_green_spotlight_on == True:
            is_green_spotlight_on = False
            greenBrightness = 0.0
            glutPostRedisplay()
        elif is_green_spotlight_on == False:
            greenBrightness = 1.0
            is_green_spotlight_on = True
            glutPostRedisplay()
        texturedPictureCheck()
    elif key == b'3':
        # Toggle blue light source
        global is_blue_spotlight_on
        if is_blue_spotlight_on == True:
            is_blue_spotlight_on = False
            blueBrightness = 0.0
            glutPostRedisplay()
        elif is_blue_spotlight_on == False:
            blueBrightness = 1.0
            is_blue_spotlight_on = True
            glutPostRedisplay()
        texturedPictureCheck()
    elif key == b'4':
        # Toggle blue light source
        global is_flash_spotlight_on
        if is_flash_spotlight_on == True:
            is_flash_spotlight_on = False
            flashBrightness = 0.0
            glutPostRedisplay()
        elif is_flash_spotlight_on == False:
            flashBrightness = 1.0
            is_flash_spotlight_on = True
            glutPostRedisplay()
        texturedPictureCheck()
    elif key == b'5':
        # Turn default light (DEBUGGING)
        global is_light_on
        is_light_on = not is_light_on
        glutPostRedisplay()
        texturedPictureCheck()
    elif key == b'6':
        # Toggle default light spotlight (DEBUGGING)
        global use_spotlight
        use_spotlight = not use_spotlight
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

    # Placing each light
    place_RedLight()
    place_GreenLight()
    place_BlueLight()

    glPushMatrix()
    glTranslated(0, 5, 0) # Moving the desk lamp light
    place_DeskLight()
    glPopMatrix()

    place_FlashLight()

    # Set up the main light (LIGHT0)... or not.
    if is_light_on:
        place_main_light()
    else:
        glDisable(GL_LIGHT0)

    # Now spin the world around the y-axis (for effect).
    # glRotated(angle_movement, 0, 1, 0)
    draw_objects()

def draw_objects():
    """Draw the objects in the scene: cylinders, spheres, floor, walls, ceilings."""
    global ROOM_LENGTH, ROOM_WIDTH, ROOM_HEIGHT

    # Draw Textured Floor
    glPushMatrix()
    glTranslate(0, 0, 15)
    glRotated(-90, 1, 0, 0)
    # draw_floor(30, 100) # Draw a floor with improved lighting effects. # DEBUGGING
    drawPlane(ROOM_WIDTH, ROOM_LENGTH, checkerBoardName)
    glPopMatrix()

    # Draw Ceiling
    glPushMatrix()
    glTranslate(0, 17, 15)
    glRotated(-90, 1, 0, 0)
    drawPlane(ROOM_WIDTH, ROOM_LENGTH, ceilingTextureName)
    glPopMatrix()

    # Draw Textured Walls (Brick)
    glPushMatrix()
    glTranslate(0, 0, 15)
    drawPlane(ROOM_WIDTH, ROOM_HEIGHT, brickTextureName) # Wall 1
    glPopMatrix()

    glPushMatrix()
    glTranslate(0, 0, -15)
    drawPlane(ROOM_WIDTH, ROOM_HEIGHT, brickTextureName) # Wall 2
    glPopMatrix()

    glPushMatrix()
    glTranslate(-15, 0, 0)
    glRotated(90, 0, 1, 0)
    drawPlane(ROOM_WIDTH, ROOM_HEIGHT, brickTextureName) # Wall 3
    glPopMatrix()

    glPushMatrix()
    glTranslate(15, 0, 0)
    glRotated(90, 0, 1, 0)
    drawPlane(ROOM_WIDTH, ROOM_HEIGHT, brickTextureName) # Wall 4
    glPopMatrix()

    # Draw Textured Picture on the wall (appears when only camera flashlight is on)
    glPushMatrix()
    glTranslate(0, 11, -14.8)
    glRotated(180, 1, 0, 0)
    texturedPictureCheck() # The picture appears based on the flag checks for the lights
    glPopMatrix()

    # Draw table
    glPushMatrix()
    glTranslate(-2, 0, -8)
    glScale(1.0, 1.0, 1.3)
    draw_table()
    glPopMatrix()

    # # Draw Desk Lamp (Doesn't display on Mac computer, but works on Windows)
    # glPushMatrix()
    # glRotated(-90, 1, 0, 0)
    # glTranslate(-3.4,-1,3.8)  # for some reason the y coordinate is where the z should be
    # draw_DeskLamp()
    # glPopMatrix()

    # Draw Copper Ball
    glPushMatrix()
    glTranslate(-5, 2.7, 2)   #0, 2, 30
    glScale(0.2, 0.2, 0.2)
    glRotated(copperBallAngle, 0, 1, 0)
    glTranslate(3, 0, 0) # Causes the ball to roll away from the y-axis
    set_copper(GL_FRONT_AND_BACK)   # Make material attributes mimic copper.
    gluSphere(ball, 1.0, 30, 30)
    glPopMatrix()

    # Draw Silver Polished Ball
    glPushMatrix()
    glTranslate(-4, 2.7, 6)  
    glScale(0.2, 0.2, 0.2)
    glRotated(silverBallAngle, 0, 1, 0)
    glTranslate(5, 0, 0) # Causes the ball to roll away from the y-axis
    set_PolishedSilver(GL_FRONT_AND_BACK)   # Make material attributes mimic silver.
    gluSphere(ball, 1.0, 30, 30)
    glPopMatrix()

    # Draw die 1
    glPushMatrix()
    glTranslate(0.5, 2.5, 5)
    glScale(0.6, 0.6, 0.6)
    glRotated(20 + diceAngle, 0, 1, 0) # Starts off slightly rotated
    draw_die()
    glPopMatrix()

    # Draw die 2
    glPushMatrix()
    glTranslate(0.8, 2.5, 3.3)
    glScale(0.6, 0.6, 0.6)
    glRotated(110 + diceAngle, 0, 1, 0) # Starts off slightly rotated
    draw_die()
    glPopMatrix()


def draw_table():
    # Draws the entire table (legs + table top)

    # Draw Leg 1 (Southwest)
    glPushMatrix()
    glTranslate(-5, 0, 11)
    glRotated(-90, 1, 0, 0)
    set_PolishedSilver(GL_FRONT_AND_BACK)   # Silver leg
    gluCylinder(tube, 0.5, 0.5, 2, 10, 10)
    glPopMatrix()

    # Draw Leg 2 (Northwest)
    glPushMatrix()
    glTranslate(-5, 0, 7)
    glRotated(-90, 1, 0, 0)
    set_pewter(GL_FRONT_AND_BACK)   # Pewter leg
    gluCylinder(tube, 0.5, 0.5, 2, 10, 10)
    glPopMatrix()

    # Draw Leg 3 (Southeast)
    glPushMatrix()
    glTranslate(3, 0, 11)
    glRotated(-90, 1, 0, 0)
    set_copper(GL_FRONT_AND_BACK)   # Copper leg
    gluCylinder(tube, 0.5, 0.5, 2, 10, 10)
    glPopMatrix()

    # Draw Leg 4 (Northeast)
    glPushMatrix()
    glTranslate(3, 0, 7)
    glRotated(-90, 1, 0, 0)
    set_pewter(GL_FRONT_AND_BACK)   # Pewter leg
    gluCylinder(tube, 0.5, 0.5, 2, 10, 10)
    glPopMatrix()

    # Draw table top
    glPushMatrix()
    glTranslate(-0.8, -2.5, 6)
    draw_table_top()
    glPopMatrix()

def draw_table_top():
    # Draw the table top (Using 6 faces/planes)

    # Top face
    glPushMatrix()
    glTranslate(0, 5, 0)
    glRotated(90, 1, 0, 0)
    drawPlane(9.5, 6, woodTextureName)
    glPopMatrix()

    # Bottom face
    glPushMatrix()
    glTranslate(0, 4.5, 0)
    glRotated(90, 1, 0, 0)
    drawPlane(9.5, 6, woodTextureName)
    glPopMatrix()

    # North side face (-z direction)
    glPushMatrix()
    glTranslate(0, 4.5, 0)
    drawPlane(9.5, 0.5, woodTextureName)
    glPopMatrix()

    # South side face (+z direction)
    glPushMatrix()
    glTranslate(0, 4.5, 6)
    drawPlane(9.5, 0.5, woodTextureName)
    glPopMatrix()

    # West side face (-x direction)
    glPushMatrix()
    glTranslate(-4.75, 4.5, 3)
    glRotated(90, 0, 1, 0)
    drawPlane(6, 0.5, woodTextureName)
    glPopMatrix()

    # East side face (+x direction)
    glPushMatrix()
    glTranslate(4.75, 4.5, 3)
    glRotated(90, 0, 1, 0)
    drawPlane(6, 0.5, woodTextureName)
    glPopMatrix()

def draw_DeskLamp(): 
    # Base of lamp
    glPushMatrix() 
    glutSolidCylinder(1, 0.5, 10, 10)
    glPopMatrix()

    # Arm of the lamp
    glPushMatrix()
    glutSolidCylinder(0.1, 3.05, 50, 50)
    glPopMatrix()

    # Neck of the lamp
    glPushMatrix()
    glTranslate(0, 0.09, 3)
    glRotated(90, 1, 0, 0)
    glutSolidCylinder(0.1, 2.5, 50, 50)
    glPopMatrix()

    # Light hood
    glPushMatrix()
    glTranslate(0, -2.5, 2.3)
    glRotated(90, 0, 0, 1)
    gluCylinder(tube, 0.5, 0.5, 1, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslate(0,-2.5,3.3)
    glRotated(90, 0, 0, 1)
    glutSolidCylinder(.5,0.01,10,10)
    glPopMatrix()

def draw_die():
    # Constructs a die using 6 planes

    # Face 1
    glPushMatrix()
    glScale(0.1, 0.1, 0.1)
    glTranslate(0, 0, 0)
    drawPlane(10, 10, die1TextureName)
    glPopMatrix()

    # Face 2
    glPushMatrix()
    glScale(0.1, 0.1, 0.1)
    glRotated(90, 1, 0, 0)
    glTranslate(0, 0, 0)
    drawPlane(10, 10, die2TextureName)
    glPopMatrix()

    # Face 3
    glPushMatrix()
    glScale(0.1, 0.1, 0.1)
    glTranslate(0, 0, 10)
    drawPlane(10, 10, die3TextureName)
    glPopMatrix()

    # Face 4
    glPushMatrix()
    glScale(0.1, 0.1, 0.1)
    glRotated(90, 1, 0, 0)
    glTranslate(0, 0, -10)
    drawPlane(10, 10, die4TextureName)
    glPopMatrix()

    # Face 5
    glPushMatrix()
    glScale(0.1, 0.1, 0.1)
    glRotated(90, 0, 1, 0)
    glTranslate(-5, 0, 5)
    drawPlane(10, 10, die5TextureName)
    glPopMatrix()

    # Face 6
    glPushMatrix()
    glScale(0.1, 0.1, 0.1)
    glRotated(90, 0, 1, 0)
    glTranslate(-5, 0, -5)
    drawPlane(10, 10, die6TextureName)
    glPopMatrix()

def draw_Textured_Picture():
    # Draw Textured Picture
    glPushMatrix()
    drawPlane(10, 8, secretPictureTextureName)
    glPopMatrix()

def place_main_light():
    """Set up the main light."""
    glMatrixMode(GL_MODELVIEW)
    lx = 3.0
    ly = rgb_light_height
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
        glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 45.0)
        glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 2.0)
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, light_direction)
    else:
        glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 180.0)
        glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 0.0)
    
    glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, use_lv)
    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
    #  Try GL_TRUE - but then watch what happens when light is low
    
    glEnable(GL_LIGHT0)

    # This part draws a SELF-COLORED sphere (in spot where light is!)
    glPushMatrix()
    glTranslatef(2, ly, 2)
    glDisable(GL_LIGHTING)
    glColor3f(brightness, brightness, brightness)
    glutSolidSphere(0.5, 20, 20)
    glEnable(GL_LIGHTING)
    glPopMatrix()

def place_DeskLight():
    """Set up the desk light (lamp)."""
    activeLight = GL_LIGHT4
    glMatrixMode(GL_MODELVIEW)
    lx = -3.3
    ly = 1.7
    lz = 3.6
    light_position = [ lx, ly, lz, 0.5 ]
    # White light
    light_ambient = [ 1 * deskBrightness, 1 * deskBrightness, 1 * deskBrightness, 1.0 ]
    light_diffuse = [ 1 * deskBrightness, 1 * deskBrightness, 1 * deskBrightness, 1.0 ]
    light_specular = [ 1 * deskBrightness, 1 * deskBrightness, 1 * deskBrightness, 1.0 ]
    light_direction = [ 0.0, -1.0, 0.0, 0.0 ]  # Light points down

    # For this light, set position, ambient, diffuse, and specular values
    glLightfv(activeLight, GL_POSITION, light_position)
    glLightfv(activeLight, GL_AMBIENT, light_ambient)
    glLightfv(activeLight, GL_DIFFUSE, light_diffuse)
    glLightfv(activeLight, GL_SPECULAR, light_specular)

    # Constant attenuation (for distance, etc.)
    # Only works for fixed light locations!  Otherwise disabled
    glLightf(activeLight, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(activeLight, GL_LINEAR_ATTENUATION, 0.0)
    glLightf(activeLight, GL_QUADRATIC_ATTENUATION, 0.000)

    # Create a spotlight effect
    if is_desk_spotlight_on:
        glLightf(GL_LIGHT4, GL_SPOT_CUTOFF, 45.0)
        glLightf(GL_LIGHT4, GL_SPOT_EXPONENT, 1.0)
        glLightfv(GL_LIGHT4, GL_SPOT_DIRECTION, light_direction)
    else:
        glLightf(GL_LIGHT4, GL_SPOT_CUTOFF,0)
        glLightf(GL_LIGHT4, GL_SPOT_EXPONENT, 0.0)

    glEnable(activeLight)

    # This part draws a SELF-COLORED sphere (in spot where light is!)
    glPushMatrix()
    glTranslatef(lx, ly, lz)
    glDisable(GL_LIGHTING)
    glColor3f(deskBrightness, deskBrightness, deskBrightness)
    glutSolidSphere(0.3, 7, 7)
    glEnable(GL_LIGHTING)
    glPopMatrix()

def place_RedLight():
    """Set up red light."""
    activeLight = GL_LIGHT1
    glMatrixMode(GL_MODELVIEW)
    lx = 0
    ly = rgb_light_height
    lz = -9
    light_position = [ lx, ly, lz, 0.8 ]
    light_ambient = [ 0.9745 * redBrightness, 0.01175 * redBrightness, 0.01175 * redBrightness, 1.0 ]
    light_diffuse = [ 0.91424 * redBrightness, 0.04136 * redBrightness, 0.04136 * redBrightness, 1.0 ]
    light_specular = [ 0.827811 * redBrightness, 0.326959 * redBrightness, 0.326959 * redBrightness, 1.0 ]
    light_direction = [ 7.0, -10.0, 5.0, 0.0 ]  # Light points down (and a little to the right)

    # For this light, set position, ambient, diffuse, and specular values
    glLightfv(activeLight, GL_POSITION, light_position)
    glLightfv(activeLight, GL_AMBIENT, light_ambient)
    glLightfv(activeLight, GL_DIFFUSE, light_diffuse)
    glLightfv(activeLight, GL_SPECULAR, light_specular)

    # Constant attenuation (for distance, etc.)
    # Only works for fixed light locations!  Otherwise disabled
    glLightf(activeLight, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(activeLight, GL_LINEAR_ATTENUATION, 0.0)
    glLightf(activeLight, GL_QUADRATIC_ATTENUATION, 0.000)

    # Create a spotlight effect
    if is_red_spotlight_on:
        glLightf(GL_LIGHT1, GL_SPOT_CUTOFF,45.0)
        glLightf(GL_LIGHT1, GL_SPOT_EXPONENT, 1.0)
        glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, light_direction)
    else:
        glLightf(GL_LIGHT1, GL_SPOT_CUTOFF,0)
        glLightf(GL_LIGHT1, GL_SPOT_EXPONENT, 0.0)
    
    glEnable(activeLight)

    # Draw RED sphere to represent the light source
    glPushMatrix()
    glTranslatef(lx,ly,lz)
    glDisable(GL_LIGHTING)
    glColor3f(redBrightness, 0, 0)
    glutSolidSphere(0.5, 20, 20)
    glEnable(GL_LIGHTING)
    glPopMatrix()

def place_GreenLight():
    """Set up the green light."""
    activeLight = GL_LIGHT2
    glMatrixMode(GL_MODELVIEW)
    lx = 4
    ly = rgb_light_height
    lz = 5
    light_position = [ lx, ly, lz, 0.8 ]
    #Emerald
    light_ambient = [ 0.0215 * greenBrightness, 0.7745 * greenBrightness, 0.0215 * greenBrightness, 1.0 ]
    light_diffuse = [ 0.07568 * greenBrightness, 0.71424 * greenBrightness, 0.07568 * greenBrightness, 1.0 ]
    light_specular = [ 0.633 * greenBrightness, 0.727811 * greenBrightness, 0.333 * greenBrightness, 1.0 ]
    light_direction = [ 3.0, -10.0, 0.0, 0.0 ]  # Light points down (and a little to the right)

    # For this light, set position, ambient, diffuse, and specular values
    glLightfv(activeLight, GL_POSITION, light_position)
    glLightfv(activeLight, GL_AMBIENT, light_ambient)
    glLightfv(activeLight, GL_DIFFUSE, light_diffuse)
    glLightfv(activeLight, GL_SPECULAR, light_specular)

    # Constant attenuation (for distance, etc.)
    # Only works for fixed light locations!  Otherwise disabled
    glLightf(activeLight, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(activeLight, GL_LINEAR_ATTENUATION, 0.0)
    glLightf(activeLight, GL_QUADRATIC_ATTENUATION, 0.000)

    # Create a spotlight effect
    if is_green_spotlight_on:
        glLightf(GL_LIGHT2, GL_SPOT_CUTOFF, 45.0)
        glLightf(GL_LIGHT2, GL_SPOT_EXPONENT, 1.0)
        glLightfv(GL_LIGHT2, GL_SPOT_DIRECTION, light_direction)
    else:
        glLightf(GL_LIGHT2, GL_SPOT_CUTOFF,0)
        glLightf(GL_LIGHT2, GL_SPOT_EXPONENT, 0.0)
    
    glEnable(activeLight)

    # Draw GREEN sphere to represent the light source
    glPushMatrix()
    glTranslatef(lx,ly,lz)
    glDisable(GL_LIGHTING)
    glColor3f(0, 1.0 * greenBrightness, 0)
    glutSolidSphere(0.5, 20, 20)
    glEnable(GL_LIGHTING)
    glPopMatrix()

def place_BlueLight():
    """Set up the blue light."""
    activeLight = GL_LIGHT3
    glMatrixMode(GL_MODELVIEW)
    lx = -4
    ly = rgb_light_height
    lz = 5
    light_position = [ lx, ly, lz, 0.8 ]
    # Bluelighting 
    light_ambient = [ 0.1 * blueBrightness, 0.18725 * blueBrightness, 0.9745 * blueBrightness, 1.0 ]
    light_diffuse = [ 0.396 * blueBrightness, 0.24151 * blueBrightness, 0.89102 * blueBrightness, 1.0 ]
    light_specular = [ 0.297254 * blueBrightness, 0.20829 * blueBrightness, 0.906678 * blueBrightness, 1.0 ]
    light_direction = [ -2.0, -10.0, 0.0, 0.0 ]  # Light points down (and a little to the right)
    # light_direction = [ 0.0, -1.0, 0.0, 0.0 ]  # Light points down

    # For Light 0, set position, ambient, diffuse, and specular values
    glLightfv(activeLight, GL_POSITION, light_position)
    glLightfv(activeLight, GL_AMBIENT, light_ambient)
    glLightfv(activeLight, GL_DIFFUSE, light_diffuse)
    glLightfv(activeLight, GL_SPECULAR, light_specular)

    # Constant attenuation (for distance, etc.)
    # Only works for fixed light locations!  Otherwise disabled
    glLightf(activeLight, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(activeLight, GL_LINEAR_ATTENUATION, 0.0)
    glLightf(activeLight, GL_QUADRATIC_ATTENUATION, 0.000)

    # Create a spotlight effect
    if is_blue_spotlight_on:
        glLightf(GL_LIGHT3, GL_SPOT_CUTOFF,55.0)
        glLightf(GL_LIGHT3, GL_SPOT_EXPONENT, 1.0)
        glLightfv(GL_LIGHT3, GL_SPOT_DIRECTION, light_direction)
    else:
        glLightf(GL_LIGHT3, GL_SPOT_CUTOFF,0)
        glLightf(GL_LIGHT3, GL_SPOT_EXPONENT, 0.0)
        
    glEnable(activeLight)

    # Draw BLUE sphere to represent the light source
    glPushMatrix()
    glTranslatef(lx,ly,lz)
    glDisable(GL_LIGHTING)
    glColor3f(0,0,blueBrightness)
    glutSolidSphere(0.5, 20, 20)
    glEnable(GL_LIGHTING)
    glPopMatrix()

def place_FlashLight():
    """Set up the flash light."""
    activeLight = GL_LIGHT5
    glMatrixMode(GL_MODELVIEW)
    lx = camera.eye.x
    ly = camera.eye.y
    lz = camera.eye.z
    light_position = [ lx, ly, lz, 1.0 ]
    # White lighting
    light_ambient = [ 1 * flashBrightness, 1 * flashBrightness, 1 * flashBrightness, 1.0 ]
    light_diffuse = [ 1 * flashBrightness, 1 * flashBrightness, 1 * flashBrightness, 1.0 ]
    light_specular = [ 1 * flashBrightness, 1 * flashBrightness, 1 * flashBrightness, 1.0 ]
    light_direction = [ 0.0, -1.0, -5.0, 0.0 ]  # Light points down
    # TODO: Make flashlight turn with camera (yaw)

    # For Light 0, set position, ambient, diffuse, and specular values
    glLightfv(activeLight, GL_POSITION, light_position)
    glLightfv(activeLight, GL_AMBIENT, light_ambient)
    glLightfv(activeLight, GL_DIFFUSE, light_diffuse)
    glLightfv(activeLight, GL_SPECULAR, light_specular)

    # Constant attenuation (for distance, etc.)
    # Only works for fixed light locations!  Otherwise disabled
    glLightf(activeLight, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(activeLight, GL_LINEAR_ATTENUATION, 0.0)
    glLightf(activeLight, GL_QUADRATIC_ATTENUATION, 0.000)

    # Create a spotlight effect
    if is_flash_spotlight_on:
        glLightf(GL_LIGHT5, GL_SPOT_CUTOFF,30.0)
        glLightf(GL_LIGHT5, GL_SPOT_EXPONENT, 1.0)
        glLightfv(GL_LIGHT5, GL_SPOT_DIRECTION, light_direction)
    else:
        glLightf(GL_LIGHT5, GL_SPOT_CUTOFF,0)
        glLightf(GL_LIGHT5, GL_SPOT_EXPONENT, 0.0)
        
    glEnable(activeLight)

    # Draw sphere to represent the light source
    # glPushMatrix()
    # glTranslatef(lx,ly,lz)
    # glDisable(GL_LIGHTING)
    # glColor3f(0,0,flashBrightness)
    # glutSolidSphere(0.5, 20, 20)
    # glEnable(GL_LIGHTING)
    # glPopMatrix()    

def drawPlane(width, height, texture):
    """ Draw a textured plane of the specified dimension. """
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE) # try GL_DECAL/GL_REPLACE/GL_MODULATE
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)           # try GL_NICEST/GL_FASTEST
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)  # try GL_CLAMP/GL_REPEAT/GL_CLAMP_TO_EDGE
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR) # try GL_LINEAR/GL_NEAREST
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
      
    # Enable/Disable each time or OpenGL ALWAYS expects texturing!
    glEnable(GL_TEXTURE_2D)
   
    ex = width/2
    sx = -ex
    ey = height
    sy = 0
    glBegin(GL_QUADS)
    glNormal3f(0, 0, 1)
    glTexCoord2f(0, 0)
    glVertex3f(sx, sy, 0)
    glTexCoord2f(width/10, 0)
    glVertex3f(ex, sy, 0)
    glTexCoord2f(width/10, height/10)
    glVertex3f(ex, ey, 0)
    glTexCoord2f(0, height/10)
    glVertex3f(sx, ey, 0)
    glEnd()
   
    glDisable(GL_TEXTURE_2D)

def generateCheckerBoardTexture():
    """
    * Generate a texture in the form of a checkerboard
    * Why?  Simple to do...
    """
    global checkerBoardName
    texture = [0]*(NROWS*NCOLS*4)
    for i in range(NROWS):
        for j in range(NCOLS):
            c = 0 if ((i&8)^(j&8)) else 255
            idx = (i*NCOLS+j)*4
            # Black/White Checkerboard
            texture[idx] = c     # Red
            texture[idx+1] = c   # Green
            texture[idx+2] = c   # Blue
            texture[idx+3] = 180 # Alpha (transparency)

    # Generate a "name" for the texture.  
    # Bind this texture as current active texture
    # and sets the parameters for this texture.
    checkerBoardName = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, checkerBoardName)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, NCOLS, NROWS, 0, GL_RGBA,
                 GL_UNSIGNED_BYTE, texture)

def loadImageTexture(filename):
    # Load the image from the file and return as a texture
    im = Image.open(filename)
    # print("Image dimensions: {0}".format(im.size))  # If you want to see the image's original dimensions
    # dim = 128
    # size = (0,0,dim,dim)
    # texture = im.crop(size).tobytes("raw")   # The cropped texture
    texture = im.tobytes("raw")   # The cropped texture
    dimX = im.size[0]
    dimY = im.size[1]
    
    returnTextureName = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, returnTextureName)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, dimX, dimY, 0, GL_RGB,
                 GL_UNSIGNED_BYTE, texture)
    return returnTextureName

# def draw_floor(size, divisions=1, f=None, df=None):
#     """Draws a floor of a given size and type.

#     Keyword arguments:
#     size -- Size of the floor (size x size grid, centered at origin)
#     divisions -- Number of divisions (default 1)
#     f -- Function to apply for the "y-height" (default None => y=0)
#     df -- Procedure to set the normal based on function f (default None)
    
#     A larger number of divisions great improves quality of the floor.
#     If df is None then the normal is set to point directly up.
#     """
#     # Be sure we are talking about correct matrix.
#     glMatrixMode(GL_MODELVIEW)
#     glPushMatrix()

#     # Make the floor mimic Pewter material.
#     set_pewter(GL_FRONT_AND_BACK)   

#     step = size / divisions
#     if f is None:
#         glNormal3f(0, 1, 0)        # Use a vertical normal.
#         glBegin(GL_QUADS)
#         for i in range(0, divisions):
#             x = -size/2 + i*step
#             for j in range(0, divisions):
#                 z = -size/2 + j*step
#                 glVertex3f(x,0,z+step)
#                 glVertex3f(x+step,0,z+step)
#                 glVertex3f(x+step,0,z)
#                 glVertex3f(x,0,z)
#         glEnd()
#     elif df is None:
#         glNormal3f(0, 1, 0)        # Use a vertical normal.
#         glBegin(GL_QUADS)
#         for i in range(0, divisions):
#             x = -size/2 + i*step
#             for j in range(0, divisions):
#                 z = -size/2 + j*step
#                 glVertex3f(x,f(x,z+step),z+step)
#                 glVertex3f(x+step,f(x+step,z+step),z+step)
#                 glVertex3f(x+step,f(x+step,z),z)
#                 glVertex3f(x,f(x,z),z)
#         glEnd()
#     else:
#         for i in range(0, divisions):
#             glBegin(GL_QUAD_STRIP)  # QUAD_STRIPS are more efficient.
#             x = -size/2 + i*step
#             for j in range(0, divisions):
#                 z = -size/2 + j*step
#                 df(x+step, z)
#                 glVertex3f(x+step,f(x+step,z),z)
#                 df(x, z)
#                 glVertex3f(x,f(x,z),z)
#             df(x+step, size/2)
#             glVertex3f(x+step,f(x+step,size/2),size/2)
#             df(x, size/2)
#             glVertex3f(x,f(x,size/2),size/2)
#             glEnd()
#     glPopMatrix()

# def drawFloor(width, height, texture):
#     """ Draw a textured floor of the specified dimension. """
#     glBindTexture(GL_TEXTURE_2D, texture)
#     glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)          # try GL_DECAL/GL_REPLACE/GL_MODULATE
#     glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)                   # try GL_NICEST/GL_FASTEST
#     glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE) # try GL_CLAMP/GL_REPEAT/GL_CLAMP_TO_EDGE
#     glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
#     glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)    # try GL_LINEAR/GL_NEAREST
#     glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

#     sx = width/2
#     ex = -sx
#     sz = height/2
#     ez = -sz
    
#     # Enable/Disable each time or OpenGL ALWAYS expects texturing!
#     glEnable(GL_TEXTURE_2D)

#     glBegin(GL_QUADS)
#     glTexCoord2f(0, 0)
#     glVertex3f(sx, 0, sz)
#     glTexCoord2f(0, 1)
#     glVertex3f(sx, 0, ez)
#     glTexCoord2f(1, 1)
#     glVertex3f(ex, 0, ez)
#     glTexCoord2f(1, 0)
#     glVertex3f(ex, 0, sz)
#     glEnd()

#     glDisable(GL_TEXTURE_2D)

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

def set_PolishedSilver(face):
    """Set the material properties of the given face to "PolishedSilver"-esque.

    Keyword arguments:
    face -- which face (GL_FRONT, GL_BACK, or GL_FRONT_AND_BACK)
    """
    ambient = [ 0.23125, 0.23125, 0.23125, 1.0]
    diffuse = [ 0.2775, 0.2775, 0.2775, 1.0]
    specular = [ 0.773911, 0.773911, 0.773911, 1.0]
    shininess = 89.6
    glMaterialfv(face, GL_AMBIENT, ambient);
    glMaterialfv(face, GL_DIFFUSE, diffuse);
    glMaterialfv(face, GL_SPECULAR, specular);
    glMaterialf(face, GL_SHININESS, shininess);


if __name__ == '__main__': main()
