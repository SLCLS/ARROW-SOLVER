import os
import time
import sys

from vision.scanner import BoardScanner
from io_utils.adb_ctrl import ADBController
from core.board import ArrowBoard
from core.solver import BoardSolver

CLAIM_BUTTON_POS = (540, 2050)

def run_bot():
    print("\n" + "="*45)
    print("   INITIALIZING FULLY AUTONOMOUS FRAMEWORK")
    print("="*45)

    scanner = BoardScanner()
    adb = ADBController()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    screenshot_path = os.path.join(script_dir, "vision", "live_screen.png")

    print("\n[READY] The bot is active.")
    print("[!] Press Ctrl+C on the terminal to stop the program process.")
    time.sleep(3)

    while True:
        start_time = time.time()

        adb.get_screenshot(screenshot_path)

        print("\n[VISION] Scanning board state...")
        board_state = scanner.scan_board(screenshot_path)
        
        game_board = ArrowBoard()
        game_board.tiles = board_state

        print("[SOLVER] Calculating optimal sequence...")
        solver = ArrowSolver(game_board, verbose=False)

        if not winning_sequence:
            print("[!] Sequence emptyy. Board iis either solved or unreadable.")
            print("[ADB] Tapping 'Claim' just in case we are stuck on the win screen...")
            adb.tap_pixel(*CLAIM_BUTTON_POS)
            time.sleep(2)
            adb.execute_sequence(winning_sequence)

            total_time = time.time() - start_time
            print(f">>> Level Cleared in {total_time:.2f} seconds! <<<")

if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n[SYSTEM\ Framework shut down safely.")