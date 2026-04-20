import time
import os
import sys
import cv2
import scrcpy

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import screen_map

def exact_sleep(duration):
    """
    Microsecond-accurate timer.
    Bypasses the Windows 15.6ms thread scheduler limit by holding the CPU hostage
    until the exact mathematical nanosecond is reached.
    """
    target = time.perf_counter() + duration
    while time.perf_counter() < target:
        pass

class ScrcpyController:
    TAP_HOLD_TIME = 0.03
    TAP_INTERVAL = 0.03
    SAME_TILE_COOLDOWN = 0.25

    def __init__(self):
        print("[SCRCPY] Booting Socket Bridge. Injecting server into device...")
        
        self.client = scrcpy.Client(max_fps=15, bitrate=2000000)
        self.client.start(threaded=True)
        
        print("[SCRCPY] Waiting for memory stream...")
        while self.client.last_frame is None:
            time.sleep(0.1)
            
        print("[SCRCPY] Stream locked. Execution bridge ready.")

    def get_screenshot(self, save_path):
        frame = self.client.last_frame
        if frame is not None:
            cv2.imwrite(save_path, frame)

    def tap_pixel(self, x, y):
        """The 'Thumb Squish' Protocol. Simulates a genuine human finger press."""

        self.client.control.touch(x, y, scrcpy.ACTION_DOWN)
        exact_sleep(self.TAP_HOLD_TIME / 2)

        self.client.control.touch(x + 2, y + 2, scrcpy.ACTION_MOVE)
        exact_sleep(self.TAP_HOLD_TIME / 2)

        self.client.control.touch(x + 2, y + 2, scrcpy.ACTION_UP)

    def execute_sequence(self, hex_sequence):
        """Fires sequence using CPU-accurate timings, not OS timings."""
        if not hex_sequence: return
        
        last_coord = None
        
        for q, r in hex_sequence:
            if (q, r) in screen_map:
                
                if (q, r) == last_coord:
                    exact_sleep(self.SAME_TILE_COOLDOWN)
                    
                x, y = screen_map[(q, r)]
                self.tap_pixel(x, y)
                
                exact_sleep(self.TAP_INTERVAL)
                last_coord = (q, r)
                
    def shutdown(self):
        self.client.stop()