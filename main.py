import os
import time
import sys

from vision.scanner import BoardScanner
from io_utils.adb_ctrl import ADBController
from core.board import ArrowBoard
from core.solver import BoardSolver

def run_bot():
    print("\n--- Initializing Arrow Solver Framework ---")
    scanner = BoardScanner()
    adb = ADBController()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    screenshot_path = os.path.join(script_dir, "vision", "live_screen.png")

    while True:
        input("\n[READY] Open the game on your phone, then press ENTER to solve (or Ctrl+C to quit)...")

        start_time = time.time()

        adb.get_screenshot(screenshot_path)

        print("[VISION] Scanning board state...")
        board_state = scanner.scan_board(screenshot_path)
        
        game_board = ArrowBoard()
        game_board.tiles = board_state

        print("[SOLVER] Calculating optimal sequence...")
        solver = ArrowSolver(game_board, verbose=False)

        if not winning_sequence:
            print("[!] Sequence emptyy. Board iis either solved or unreadable.")

            adb.execute_sequence(winning_sequence)

            total_time = time.time() - start_time
            print(f">>> Level Cleared in {total_time:.2f} seconds! <<<")

if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n[SYSTEM\ Framework shut down safely.")