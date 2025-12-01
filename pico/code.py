import machine
import time

#rows (Shared across all arrows), sets up the rows and maps on the GPIO pins, 
ROW_PINS = [0, 1, 2]

#Creates the column pins for each arrow direction, so if GPI3 or  is pressed, it means the up arrow is pressed
#if 
COL_PINS = [
    3, 4, 5, #up Arrow Cols
    6, 7, 8, #right Arrow Cols
    9, 10, 11, #down Arrow Cols
    12, 13, 14 #left Arrow Cols
]

#mappings on the tiles to numbers
TILE_UP    = 0
TILE_RIGHT = 1
TILE_DOWN  = 2
TILE_LEFT  = 3

#map the raw column index (0-11) to the specific Tile Bucket
COL_TO_TILE_MAP = {
    0: TILE_UP, 1: TILE_UP, 2: TILE_UP,
    3: TILE_RIGHT, 4: TILE_RIGHT, 5: TILE_RIGHT,
    6: TILE_DOWN, 7: TILE_DOWN, 8: TILE_DOWN,
    9: TILE_LEFT, 10: TILE_LEFT, 11: TILE_LEFT
}

#uses for loops to create the row objects
rows = []
for p in ROW_PINS:
    pin = machine.Pin(p, machine.Pin.IN)
    rows.append(pin)

#uses for loop to create the column objects 
cols = []
for p in COL_PINS:
    pin = machine.Pin(p, machine.Pin.IN, machine.Pin.PULL_UP)
    cols.append(pin)

#Used to limit serial spam
last_print_state = ""

print("DDR Pad Ready. Waiting for steps...")

while True:
    #starts from the top, and begins to scan and has everything set to false
    #which means not pressed
    #0 = False/off, 1 = True/on
    current_scan_state = [0, 0, 0, 0]
    #scans the Matrix
    for r_idx, row in enumerate(rows):
        row.init(machine.Pin.OUT)
        row.value(0)
        #tiny delay for stability
        time.sleep_us(30)

        for c_idx, col in enumerate(cols):
            if col.value() == 0: #pressed (Active Low)
                tile_id = COL_TO_TILE_MAP[c_idx]
                current_scan_state[tile_id] = 1
        
        row.init(machine.Pin.IN)
    #send the Serial Data to Visualizer
    #only print if the state actually changed to keep USB fast
    #format: STATE: 1,0,0,1
    state_str = f"{current_scan_state[0]},{current_scan_state[1]},{current_scan_state[2]},{current_scan_state[3]}"
    
    if state_str != last_print_state:
        print(f"STATE:{state_str}")    #this is what gets sent over USB serial
        last_print_state = state_str
    time.sleep_ms(1)

    #Scans the touch pad wired as 3 rows (GP0–GP2) × 12 columns (GP3–GP14).
    #Maps columns into 4 tiles: [UP, RIGHT, DOWN, LEFT].
    #For each scan, builds a 4-element list like [1,0,0,1] (1 = tile pressed).
    #When this pattern changes, prints a line over USB serial:
    #STATE:1,0,0,1
