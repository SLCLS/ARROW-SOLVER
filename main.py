import os
import time
import sys
import datetime

from vision.scanner import BoardScanner
from io_utils.adb_ctrl import ADBController
from core.board import ArrowBoard
from core.solver import ArrowSolver
from core.validator import is_board_solved
from config import screen_map

STARS_PER_SOLVE = 11258

def get_dynamic_claim_pos():
    """Calculates the Claim button position dynamically based on screen resolution."""

    center_x = screen_map[(0, 0)][0]

    tile_spacing = screen_map[(0, 1)][1] - screen_map[(0, 0)][1]

    bottom_y = screen_map[(0, 3)][1]

    claim_y = int(bottom_y + (tile_spacing * 1.5))
    
    return (center_x, claim_y)

CLAIM_BUTTON_POS = get_dynamic_claim_pos() 

class StatsLogger:
    def __init__(self, log_path):
        self.log_path = log_path
        self.total_solves = 0
        self.total_time = 0.0
        self._load_history()

    def _load_history(self):
        """Parses existing logs to maintain persistent statistics."""
        if not os.path.exists(self.log_path):
            return
            
        with open(self.log_path, 'r') as f:
            for line in f:
                if line.startswith("[ ") and " ] — " in line:
                    try:
                        time_str = line.split(" — ")[1].split("s @")[0]
                        self.total_time += float(time_str)
                        self.total_solves += 1
                    except Exception:
                        pass 

    def log_run(self, time_taken):
        """Writes the individual run to the file and updates terminal stats."""
        self.total_solves += 1
        self.total_time += time_taken
        
        now = datetime.datetime.now()
        dt_str = now.strftime("%m/%d %H:%M:%S")

        log_line = f"[ {self.total_solves:06d} ] — {time_taken:.2f}s @ {dt_str}\n"
        
        with open(self.log_path, 'a') as f:
            f.write(log_line)
            
        self._print_terminal_stats(time_taken)

    def _print_terminal_stats(self, last_time):
        avg_time = self.total_time / self.total_solves
        total_stars = self.total_solves * STARS_PER_SOLVE
        
        print(f">>> Level Solved in {last_time:.2f} seconds <<<")
        print(f"    [STAT] Total Solves: {self.total_solves} | Avg Time: {avg_time:.2f}s | Stars: {total_stars:,}")

    def write_session_end(self):
        """Stamps a statistics footer to the log file on shutdown."""
        if self.total_solves == 0:
            return
            
        avg_time = self.total_time / self.total_solves
        total_stars = self.total_solves * STARS_PER_SOLVE
        
        with open(self.log_path, 'a') as f:
            f.write(f"\n--- SESSION END ---\n")
            f.write(f"Total Solves: {self.total_solves}\n")
            f.write(f"Average Time: {avg_time:.2f}s\n")
            f.write(f"Total Stars:  {total_stars:,}\n")
            f.write(f"-------------------\n\n")

def run_bot(logger):
    print("\n" + "="*45)
    print("   INITIALIZING AUTONOMOUS FRAMEWORK v2.0")
    print("="*45)
    
    scanner = BoardScanner()
    adb = ADBController()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    screenshot_path = os.path.join(script_dir, "vision", "live_screen.png")

    print(f"\n[SYSTEM] History loaded. Previous Solves: {logger.total_solves}")
    print("[READY] The bot is searching for targets...")
    time.sleep(2)

    while True:
        level_solved = False
        
        while not level_solved:
            start_time = time.time()
            
            adb.get_screenshot(screenshot_path)
            print("\n[VISION] Scanning board state...")
            board_state = scanner.scan(screenshot_path)
            
            if is_board_solved(board_state):
                print("[VALIDATOR] Board is confirmed SOLVED.")
                level_solved = True
                break
            
            game_board = ArrowBoard()
            game_board.tiles = board_state 
            
            solver = ArrowSolver(game_board, verbose=False)
            winning_sequence = solver.solve()
            
            if not winning_sequence:
                print("[!] Solver returned no moves. Possible transition state. Retrying...")
                time.sleep(1)
                continue
                
            print(f"[SOLVER] Sequence locked: {len(winning_sequence)} taps.")
            adb.execute_sequence(winning_sequence)
            
            total_time = time.time() - start_time
            logger.log_run(total_time)

            print("[AUTO] Waiting for tiles to settle...")
            time.sleep(0.25)
            
            print("[VALIDATOR] Re-scanning for verification...")
        
        print("[AUTO] Animations finished. Proceeding to next level.")
        time.sleep(0.25) 
        
        print("[ADB] Tapping 'Claim Stars' button...")
        adb.tap_pixel(*CLAIM_BUTTON_POS)
        
        print("[AUTO] Waiting for next level to fade in...")
        time.sleep(0.25)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_dir, "logs.txt")

    bot_logger = StatsLogger(log_file_path)
    
    try:
        run_bot(bot_logger)
    except KeyboardInterrupt:
        print("\n\n[SYSTEM] Kill switch activated. Framework shut down safely.")
        bot_logger.write_session_end()
        print("[SYSTEM] Session statistics written to logs.txt")