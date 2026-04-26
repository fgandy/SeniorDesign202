import time
import struct
import win32file
import keyboard


# CONFIGURATION

PIPE_NAME = r"\\.\pipe\HandOfLesser"
PACKET_TYPE_BOOL = 602
PACKET_TYPE_FLOAT = 601

# Hand IDs
HAND_LEFT = 0
HAND_RIGHT = 1

# PIPE CONNECTION

print(f"Attempting to connect to {PIPE_NAME}...")
try:
    handle = win32file.CreateFile(
        PIPE_NAME,
        win32file.GENERIC_WRITE,
        0, None,
        win32file.OPEN_EXISTING,
        0, None
    )
    print("SUCCESS: Connected to Driver!")
except Exception as e:
    print(f"ERROR: Could not connect. (Ensure SteamVR is running and HandOfLesser.exe is CLOSED).")
    exit()


# DATA HELPERS

def send_bool(side, path, value):
    name_bytes = path.encode('utf-8').ljust(64, b'\x00')
    data = struct.pack("@ii64s?xxx", PACKET_TYPE_BOOL, side, name_bytes, value)
    win32file.WriteFile(handle, data)

def send_float(side, path, value):
    name_bytes = path.encode('utf-8').ljust(64, b'\x00')
    data = struct.pack("@ii64sf", PACKET_TYPE_FLOAT, side, name_bytes, float(value))
    win32file.WriteFile(handle, data)

def update_hand(side, joy_x, joy_y, joy_click, trigger, grip, btn_primary, btn_secondary, btn_system, btn_menu):
    # 1. JOYSTICK
    joy_touch = (joy_x != 0.0) or (joy_y != 0.0) or joy_click
    send_bool(side, "/input/joystick/touch", joy_touch)
    send_bool(side, "/input/joystick/click", joy_click)
    send_float(side, "/input/joystick/x", joy_x)
    send_float(side, "/input/joystick/y", joy_y)

    # 2. TRIGGER (Shoot)
    send_bool(side, "/input/trigger/touch", trigger)
    send_bool(side, "/input/trigger/click", trigger)
    send_float(side, "/input/trigger/value", 1.0 if trigger else 0.0)

    # 3. GRIP (Grab)
    send_bool(side, "/input/grip/touch", grip)
    send_bool(side, "/input/grip/click", grip)
    send_float(side, "/input/grip/value", 1.0 if grip else 0.0)

    # 4. BUTTONS (A/B or X/Y)
    send_bool(side, "/input/a/touch", btn_primary)
    send_bool(side, "/input/a/click", btn_primary)

    send_bool(side, "/input/b/touch", btn_secondary)
    send_bool(side, "/input/b/click", btn_secondary)

    # 5. SYSTEM / MENU BUTTONS
    # Note: "/input/system/click" usually opens the SteamVR Dashboard
    # Note: "/input/menu/click" usually opens the Game Menu
    send_bool(side, "/input/system/touch", btn_system)
    send_bool(side, "/input/system/click", btn_system)
    
    send_bool(side, "/input/menu/touch", btn_menu)
    send_bool(side, "/input/menu/click", btn_menu)


# MAIN LOOP

print("------------------------------------------------")
print(" FULL DUAL CONTROLLER BRIDGE ACTIVE")
print(" Left:  WASD + L-Shift/Ctrl + 1/2 + Tab(Menu)")
print(" Right: Arrows + Space/R-Shift + Enter/Bksp + End(Sys)")
print(" [ESC] to Quit")
print("------------------------------------------------")

while True:
    if keyboard.is_pressed('esc'):
        break

    # --- READ LEFT HAND (Side 0) ---
    l_x = 0.0
    l_y = 0.0
    if keyboard.is_pressed('w'): l_y = 1.0
    if keyboard.is_pressed('s'): l_y = -1.0 
    if keyboard.is_pressed('d'): l_x = 1.0
    if keyboard.is_pressed('a'): l_x = -1.0 
    
    update_hand(
        side=HAND_LEFT,
        joy_x=l_x,
        joy_y=l_y,
        joy_click=keyboard.is_pressed('ctrl'),
        trigger=keyboard.is_pressed('q'),
        grip=keyboard.is_pressed('shift'),
        btn_primary=keyboard.is_pressed('1'),   # Button X
        btn_secondary=keyboard.is_pressed('2'), # Button Y
        btn_system=False,                       # Left usually doesn't use System
        btn_menu=keyboard.is_pressed('tab')     # Left Menu Button (3 Lines)
    )

    # --- READ RIGHT HAND (Side 1) ---
    r_x = 0.0
    r_y = 0.0
    if keyboard.is_pressed('up'):    r_y = 1.0
    if keyboard.is_pressed('down'):  r_y = -1.0
    if keyboard.is_pressed('right'): r_x = 1.0
    if keyboard.is_pressed('left'):  r_x = -1.0

    update_hand(
        side=HAND_RIGHT,
        joy_x=r_x,
        joy_y=r_y,
        joy_click=keyboard.is_pressed('right ctrl'),
        trigger=keyboard.is_pressed('space'),
        grip=keyboard.is_pressed('e'),
        btn_primary=keyboard.is_pressed('enter'),  # Button A
        btn_secondary=keyboard.is_pressed('backspace'),  # Button B
        btn_system=keyboard.is_pressed('end'),           # Right System Button (Oculus Logo)
        btn_menu=False
    )

    time.sleep(0.00001)
