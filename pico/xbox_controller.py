#!/usr/bin/env python3
import uinput

class XboxController:
    def __init__(self):
        self.device = uinput.Device([
            uinput.BTN_DPAD_UP,
            uinput.BTN_DPAD_DOWN,
            uinput.BTN_DPAD_LEFT, 
            uinput.BTN_DPAD_RIGHT,
        ])
        print("Xbox Controller Ready")
    
    def up_press(self):
        self.device.emit(uinput.BTN_DPAD_UP, 1)
    
    def up_release(self):
        self.device.emit(uinput.BTN_DPAD_UP, 0)
    
    def down_press(self):
        self.device.emit(uinput.BTN_DPAD_DOWN, 1)
    
    def down_release(self):
        self.device.emit(uinput.BTN_DPAD_DOWN, 0)
        
    def left_press(self):
        self.device.emit(uinput.BTN_DPAD_LEFT, 1)
    
    def left_release(self):
        self.device.emit(uinput.BTN_DPAD_LEFT, 0)
        
    def right_press(self):
        self.device.emit(uinput.BTN_DPAD_RIGHT, 1)
    
    def right_release(self):
        self.device.emit(uinput.BTN_DPAD_RIGHT, 0)

# Global instance
controller = XboxController()




'''
from xbox_controller import controller

# In your sensor detection logic:
if up_sensor_touched:
    controller.up_press()
elif up_sensor_released:
    controller.up_release()

if down_sensor_touched:
    controller.down_press() 
elif down_sensor_released:
    controller.down_release()

if right_sensor_touched:
    controller.right_press()
elif right_sensor_released:
    controller.right_release()

if left_sensor_touched:
    controller.left_press()
elif left_sensor_released:
    controller.left_release()

'''