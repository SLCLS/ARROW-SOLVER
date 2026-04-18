import subprocess
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import screen_map

class ADBController:
    def __init__(self):

        try:
            res = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True)
            if "device\n" not in res.stdout and "device\r\n" not in res.stdout:
                print("[WARNING] No ADB device detected. Ensure USB debugging is on.")
        except FileNotFoundError:
            raise RuntimeError("ADB is not installed or not in your system PATH.")

    def tap(self, q, r):
        """Executes a single tap (Useful for testing)."""
        if (q, r) not in screen_map:
            raise ValueError(f"Coordinate {(q, r)} is not mapped in screen_map.")
        
        x, y = screen_map[(q, r)]
        cmd = ["adb", "shell", "input", "tap", str(x), str(y)]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def tap_pixel(self, x, y):
        """Executes a direct tap on raw physical (x, y) pixels."""
        cmd = ["adb", "shell", "input", "tap", str(x), str(y)]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def execute_sequence(self, hex_sequence):
        """
        Takes a list of (q, r) tuples and executes them in a single, high-speed batch.
        """
        if not hex_sequence:
            return

        print(f"\n--- Executing {len(hex_sequence)} Moves ---")
        
        commands = []
        for q, r in hex_sequence:
            if (q, r) not in screen_map:
                print(f"[ERROR] Solver outputted unmapped hex {(q, r)}. Skipping.")
                continue
            
            x, y = screen_map[(q, r)]
            commands.append(f"input tap {x} {y}")

        batch_string = "; ".join(commands)

        start_time = time.time()
        subprocess.run(["adb", "shell", batch_string])
        end_time = time.time()
        
        print(f"[SUCCESS] Sequence executed in {end_time - start_time:.2f} seconds.")
    
    def get_screenshot(self, save_path):
        """Captures the Android screen and saves it directly to the PC."""
        print("[ADB] Capturing screen...")

        subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/bot_screen.png"], stdout=subprocess.DEVNULL)
        subprocess.run(["adb", "pull", "/sdcard/bot_screen.png", save_path], stdout=subprocess.DEVNULL)

if __name__ == "__main__":
    adb = ADBController()
    
    print("Testing single tap on Center tile (0,0)...")
    adb.tap(0, 0)
    time.sleep(1)
    
    print("Testing rapid batch tap on Top-Left corner...")
    test_sequence = [(-3, 0), (-3, 1), (-3, 2)]
    adb.execute_sequence(test_sequence)