import serial
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
import time
from pynput.keyboard import Key, Controller

SERIAL_PORT = '/dev/ttyACM0' 
BAUD_RATE = 115200

keyboard = Controller()

#map data indices to actual Keys
#order from Pico: [UP, RIGHT, DOWN, LEFT]
KEY_MAPPING = [Key.up, Key.right, Key.down, Key.left]

def draw_controller(device, states):
    """
    Draws 4 directional squares (DDR Style) based on state.
    states order: [UP, RIGHT, DOWN, LEFT]
    1 = Pressed (White), 0 = Released (Black)
    """
    with canvas(device) as draw:
        box_size = 18
        center_x = device.width // 2 #divided by 2 and rounds down 
        center_y = device.height // 2
        
        #define coordinates, the left, top, right and bottom
        up_box = (center_x - box_size//2, 0, center_x + box_size//2, box_size)
        right_box = (center_x + box_size, center_y - box_size//2, center_x + 2*box_size, center_y + box_size//2)
        down_box = (center_x - box_size//2, device.height - box_size - 1, center_x + box_size//2, device.height - 1)
        left_box = (center_x - 2*box_size, center_y - box_size//2, center_x - box_size, center_y + box_size//2)

        #labels for individual char values
        coords = [up_box, right_box, down_box, left_box]
        labels = ["U", "R", "D", "L"]

        #iterates through each of the boxes
        for i in range(4):
            #pressed state is '1'
            is_pressed = (states[i] == '1')
            if is_pressed:
                #pressed:solid White Box, Black Text
                draw.rectangle(coords[i], outline="white", fill="white")
                w, h = draw.textsize(labels[i])
                text_x = (coords[i][0] + coords[i][2]) // 2 - w // 2
                text_y = (coords[i][1] + coords[i][3]) // 2 - h // 2
                draw.text((text_x, text_y), labels[i], fill="black")
            else:
                #released:black Box with White Outline
                draw.rectangle(coords[i], outline="white", fill="black")
                w, h = draw.textsize(labels[i])
                text_x = (coords[i][0] + coords[i][2]) //2 - w // 2
                text_y = (coords[i][1] + coords[i][3]) // 2 - h // 2
                draw.text((text_x, text_y), labels[i], fill="white")
def main():
    try:
        print("Initializing OLED...")
        i2c_bus = i2c(port=1, address=0x3C)
        device = sh1106(i2c_bus, rotate=0)
        device.clear()

        print(f"Connecting to Pico on {SERIAL_PORT}...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1) #open the same USB serial
        ser.flush()
        print("Connected! Waiting for 'STATE:' messages...")

        current_states = ['0', '0', '0', '0']
        current_key_state = [False, False, False, False]
        
        draw_controller(device, current_states)
        
        while True:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8').strip() #read what Pico printed
                    #parse only lines starting with "STATE:"
                    if line.startswith("STATE:"):
                        #remove prefix and whitespace
                        clean_data = line.replace("STATE:", "").strip()
                        #split into list ["1", "0", "0", "0"]
                        new_states = clean_data.split(',')
                        #valid data check (must have 4 items)
                        if len(new_states) == 4:
                            #update OLED if changed
                            if new_states != current_states: #if the data is different from the last time, then
                                current_states = new_states

                                draw_controller(device, current_states)
                                print(f"Pad Update: {current_states}")

                            #preses the keys on Computer
                            for i in range(4):
                                is_active = (new_states[i] == '1')
                                #if active now, but wasn't before -> PRESS
                                if is_active and not current_key_state[i]:
                                    keyboard.press(KEY_MAPPING[i])
                                    current_key_state[i] = True #presses the key
                                #if inactive now, but was before -> RELEASE
                                elif not is_active and current_key_state[i]:
                                    keyboard.release(KEY_MAPPING[i])
                                    current_key_state[i] = False
                        else:
                            #ignore malformed lines
                            pass
                except UnicodeDecodeError:
                    pass #ignores random serial noise
            #short sleep to prevent CPU hogging
            time.sleep(0.005) 


    except serial.SerialException:
        print(f"Error: Could not connect to {SERIAL_PORT}. Check your cable/port.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
        if 'device' in locals():
            device.clear()
        print("Exiting.")
if __name__ == "__main__":
    main()
