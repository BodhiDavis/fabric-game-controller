import serial
import time
import os

# --- SYSTEM CONFIG ---
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200

# --- GRID CONFIG ---
CELL_SIZE = 10
CELL_GAP = 2
GRID_COLS = 5
GRID_ROWS = 5 # Display a 5x5 grid, ignoring the first row from the pico

GRID_WIDTH = (CELL_SIZE * GRID_COLS) + (CELL_GAP * (GRID_COLS - 1))
GRID_HEIGHT = (CELL_SIZE * GRID_ROWS) + (CELL_GAP * (GRID_ROWS - 1))

def draw_grid(grid_states):
    """Draw the entire grid in the terminal based on the current states."""
    # Clear screen and move cursor to top
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("=" * (GRID_COLS * 4 + 1))
    print("Touch Grid (■ = touched, □ = not touched)")
    print("=" * (GRID_COLS * 4 + 1))
    
    for r in range(GRID_ROWS):
        row_str = "║"
        for c in range(GRID_COLS):
            index = r * GRID_COLS + c
            
            # '0' means touch (LOW), '1' means no touch
            if index < len(grid_states) and grid_states[index] == '0':
                row_str += " ■ "
            else:
                row_str += " □ "
            row_str += "║"
        print(row_str)
        
        # Print separator between rows
        if r < GRID_ROWS - 1:
            print("║" + "═══║" * GRID_COLS)
    
    print("=" * (GRID_COLS * 4 + 1))

def main():
    ser = None
    try:
        print(f"Connecting to Raspberry Pi Pico on {SERIAL_PORT}...")
        # --- OPTIMIZATION: Reduce timeout to prevent long hangs ---
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        ser.flush()
        print("Connection successful. Reading 5x5 grid from Pico...")

        # Initialize with an empty grid state
        grid_states = ['1'] * (GRID_ROWS * GRID_COLS)
        
        # --- OPTIMIZATION: Draw the initial empty grid once ---
        draw_grid(grid_states)
        
        while True:
         # Check if there's data waiting in the serial buffer
         if ser.in_waiting > 0:
             try:
                 line = ser.readline().decode('utf-8').strip()
                 print(f"\nReceived: {line}")  # Debug output
                 
                 # Ensure the line is not empty and has the correct format
                 if line and line.count(',') == (6 * 5 - 1):
                     # We receive a 6x5 grid, but only process a 5x5 grid
                     full_grid = line.split(',')
                     new_states = full_grid[5:] # Skip the first 5 values (row 0)
                     
                     # --- OPTIMIZATION: Only redraw if the state has changed ---
                     if new_states != grid_states:
                         grid_states = new_states
                         draw_grid(grid_states)
                         
             except UnicodeDecodeError:
                 # Handle cases where incomplete data is read
                 print("Warning: UnicodeDecodeError. Flushing input.")
                 ser.reset_input_buffer()
            
        # Sleep briefly to yield CPU time. 20Hz = 50ms.
        # We can sleep for less to ensure high responsiveness.
        time.sleep(0.02) # Loop at ~50Hz

    except serial.SerialException as e:
        print(f"Error: Could not open serial port {SERIAL_PORT}. {e}")
    except FileNotFoundError:
        print(f"Error: Serial port {SERIAL_PORT} not found.")
    except KeyboardInterrupt:
        print("\nProgram stopped.")
    finally:
        if ser is not None and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
