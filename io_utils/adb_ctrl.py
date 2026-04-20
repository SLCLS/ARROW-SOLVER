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
        if not hex_sequence: return
        commands = []
        for q, r in hex_sequence:
            if (q, r) in screen_map:
                x, y = screen_map[(q, r)]
                # Swipe from X,Y to X,Y in 1 millisecond. It registers as a hyper-fast tap.
                commands.append(f"input swipe {x} {y} {x} {y} 1")

        batch_string = "; ".join(commands)
        subprocess.run(["adb", "shell", batch_string])
    
    def get_screenshot(self, save_path):
        with open(save_path, "wb") as f:
            subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=f)

    def shutdown(self):
        """Dummy method to satisfy polymorphic execution alongside ScrcpyController."""
        pass

if __name__ == "__main__":
    adb = ADBController()
    
    print("Testing single tap on Center tile (0,0)...")
    adb.tap(0, 0)
    time.sleep(1)
    
    print("Testing rapid batch tap on Top-Left corner...")
    test_sequence = [(-3, 0), (-3, 1), (-3, 2)]
    adb.execute_sequence(test_sequence)