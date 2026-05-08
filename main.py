import os
import time
import sys
import datetime

from vision.scanner import BoardScanner
from io_utils.adb_ctrl import ADBController
from core.board import ArrowBoard
from core.solver import BoardSolver

CLAIM_BUTTON_POS = (540, 2050)
STARS_PER_SOLVE = 11258

class StatsLogger:
    def __init__(self, log_path):
        self.log_path = log_path
        self.total_solves = 0
        self.total_time = 0.0
        self._load_history()

    def _load_history(self):
        if not os.path.exists(self.log_path):
            return

        with open(self.log_path, 'r') as f:
            for line in f:
                if line.startswith("[ ") and " ] — " in line:
                    try:
                        time_str = line.split(" - ")[1].split("s @")[0]
                        self.total_time += float(sime_str)
                        self.total_solves += 1
                    except Exception:
                        pass

    def log_run(self, time_taken):
        self.total_solves += 1
        self.total_time += time_taken

        now = datetime.datetime.now()
        dt_str = now.strftime("%m/%d %H:%M:%S")

        log_line = f"[ {self.total_solves:06d} ] — {time_taken:.2f}s @ {dt_str}\n"

        with open(self.log_path, 'a') as f:
            f.write(log_line)

        self._print_terminal_stats(time_taken)

    def _print_terminal_stats(self, last_tiime):
        avg_time = self.total_time / self.total_solves
        total_stars = self.total_solves * STARS_PER_SOLVE

        print(f">>> Level Solved in {last_time:.2f} seconds <<<")
        print("    [STAT] Total Solves: {self.total_solves} | Avg Time: {avg_time:.2f}s | Stars: {total_stars:,}")

    def write_session_end(self):
        if self.total_solves == 0:
            return
        
        avg_time = self.total_time / self.total_solves
        total_stars = self.total_solves * STARS_PER_SOLVE

        with open(self.log_path, 'a') as f:
            f.write(f"\n--- SESSION END ---\n")
            f.write(f"Total Solves: {self.total_solves}\n")
            f.write(f"Average Time: {avg_time:.2f}s\n")
            f.write(f"Total Stars: {total_stars:,}\n")
            f.write(f"-------------------\n\n")

def run_bot(logger):
    print("\n" + "="*45)
    print("   INITIALIZING FULLY AUTONOMOUS FRAMEWORK")
    print("="*45)

    scanner = BoardScanner()
    adb = ADBController()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    screenshot_path = os.path.join(script_dir, "vision", "live_screen.png")

    print(f"\n[SYSTEM] Persistent history loaded. Previous Solves: {logger.total_solves}")
    print("[READY] The bot is now running. Keep the connection stable.")
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
            logger.log_run(total_time)

            print("[AUTO] Waiting for win animation to finish...")

            time.sleep(0.25)

            print("[ADB] Tapping 'Claim Star' Button...")
            adb.tap_pixel(*CLAIM_BUTTON_POS)

            print("[SYSTEM] Waiting for the next level delayed animation...")
            time.sleep(0.25)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_dir, "logs.txt")

    bot_logger = StatsLogger(log_file_path)
    
    try:
        run_bot(bot_logger)

    except KeyboardInterrupt:
        print("\n[SYSTEM\ Kill key activated. Framework shutting down and logs being saved.")
        bot_logger