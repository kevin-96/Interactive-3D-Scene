# Interactive-3D-Scene

TEAM MEMBERS:
Phillip Nam, Kevin Sangurima, Ryan Clark


HOW TO RUN THE PROGRAM:
1. Unzip the project file ("Interactive3DScene.zip")
2. Using a terminal, navigate to the folder that was unzipped
3. In that folder, run the following command "python3 lightRoom3D.py" (Make sure Python is installed on your machine! Also, import OpenGL and PIL libraries)


NOTES (IMPORTANT!!!):
- Camera flashlight can be toggled on/off and it moves up, down, left, and right. Unfortunately, at the moment it doesn't turn with the camera's horizontal look angle (yaw). It points in the -z direction only.
- (IMPORTANT) The lamp doesn't load on Mac (not sure if its due to Mac or FreeGlut version), but the lamp loads on Windows. For Mac, if you uncomment the lamp being drawn in "draw_objects" method, scene will load.
- For Mac, on line 154. multiply win_width and win_height by 2 in order to display scene correctly.


HOW TO INTERACT WITH THE SCENE:

'h' = Display help message (in console)

Camera Movement Controls:
'w' = Move forward
's' = Move backward
'a' = Move left (side to side)
'd' = Move right (side to side)
'q' = Look left
'e' = Look right
'z' = Look down
'c' = Look up
'x' = Look straight ahead (Set gaze level straight)
't' = Go back to starting position
'+' = Ascend (DEBUG)
'-' = Descend (DEBUG)

Light:
'0' = Toggle desk lamp on/off
'1' = Toggle red light on/off
'2' = Toggle green light on/off
'3' = Toggle blue light on/off
'4' = Toggle camera flashlight on/off
'5' = Toggle main light on/off (DEBUG) - see the entire room lit up
'6' = Toggle main light spotlight on/off (DEBUG)

Animation:
'j' = Toggle rolling copper ball on/off
'k' = Toggle rolling silver ball on/off
'l' = Toggle dice animation (can't press button again until animation ends)

EXTRA FEATURES:
'r' = (Yaw) Turn 180 degrees - Don't waste time pressing 'q' or 'e' repeatedly :)
