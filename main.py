import os
import time
import sys
import subprocess
import datetime
import config

from vision.scanner import BoardScanner
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

def install_scrcpy_dependencies():
    """Handles strict dependency downgrades for Windows PyAV bypass."""
    print("\n" + "!"*45)
    print(" [WARNING] STRICT DEPENDENCIES REQUIRED")
    print("!"*45)
    print("The Scrcpy Socket Bridge requires forced dependency downgrades")
    print("to bypass a known Windows C++ compilation wall.")
    print("\nThis will install:")
    print("  - scrcpy-client (latest)")
    print("  - av (latest)")
    print("  - adbutils == 0.14.1 (DOWNGRADE)")
    print("  - setuptools == 69.5.1 (DOWNGRADE)")
    
    confirm = input("\nProceed with auto-installation? (Y/n): ").strip().lower()
    if confirm == 'n':
        print("[SYSTEM] Scrcpy installation aborted. Defaulting to ADB mode.")
        return False

    print("\n[SYSTEM] Initiating dependency injection. Please wait...")
    
    subprocess.run([sys.executable, "-m", "pip", "install", "av", "adbutils"], check=False)
    subprocess.run([sys.executable, "-m", "pip", "install", "scrcpy-client", "--no-deps"], check=False)
    subprocess.run([sys.executable, "-m", "pip", "install", "adbutils==0.14.1", "setuptools==69.5.1"], check=False)
    
    io_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "io_utils")
    os.makedirs(io_dir, exist_ok=True)
    txt_path = os.path.join(io_dir, "SCRCPY.txt")
    
    with open(txt_path, "w") as f:
        f.write("# Auto-generated Scrcpy Bridge Requirements\n")
        f.write("scrcpy-client\n")
        f.write("av\n")
        f.write("adbutils==0.14.1\n")
        f.write("setuptools==69.5.1\n")
        
    print(f"\n[SYSTEM] Dependencies locked. Manifest generated at io_utils/SCRCPY.txt")
    return True

def get_execution_mode():
    """Checks config.py for saved mode or prompts the user on first run."""
    if hasattr(config, "EXECUTION_MODE"):
        return config.EXECUTION_MODE

    print("\n" + "="*45)
    print("   EXECUTION MODE SELECTION (config.py)")
    print("="*45)
    print("Select how the framework should communicate with the device:")
    print("  [1] Standard ADB (Default, Stable, No extra dependencies)")
    print("  [2] Scrcpy Socket (Experimental, Unstable, Low latency)")
    
    while True:
        choice = input("\nEnter 1 or 2 (Default: 1): ").strip()
        if choice in ["", "1"]:
            mode = "ADB"
            break
        elif choice == "2":
            success = install_scrcpy_dependencies()
            if success:
                mode = "SCRCPY"
            else:
                mode = "ADB" 
            break
        else:
            print("[!] Invalid input. Please enter 1 or 2.")

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.py")
    with open(config_path, "a") as f:
        f.write(f"\n\nEXECUTION_MODE = '{mode}'")

    print(f"\n[SYSTEM] Mode permanently saved to config.py. You can edit it there directly.")
    return mode

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
                        time_str = line.split(" — ")[1].split("s @")[0]
                        self.total_time += float(time_str)
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

    def _print_terminal_stats(self, last_time):
        avg_time = self.total_time / self.total_solves
        total_stars = self.total_solves * STARS_PER_SOLVE
        print(f">>> Level Solved in {last_time:.2f} seconds <<<")
        print(f"    [STAT] Total Solves: {self.total_solves} | Avg Time: {avg_time:.2f}s | Stars: {total_stars:,}")

    def write_session_end(self):
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
    print("   INITIALIZING AUTONOMOUS FRAMEWORK v3.0")
    print("="*45)
    
    scanner = BoardScanner()
    mode = get_execution_mode()
    
    if mode == "SCRCPY":
        try:
            from io_utils.scrcpy_ctrl import ScrcpyController
            io_controller = ScrcpyController()
            print("[SYSTEM] Scrcpy Socket Bridge initialized.")
        except ImportError:
            print("[!] io_utils/scrcpy_ctrl.py not found or dependencies missing. Falling back to ADB.")
            from io_utils.adb_ctrl import ADBController
            io_controller = ADBController()
    else:
        from io_utils.adb_ctrl import ADBController
        io_controller = ADBController()
        print("[SYSTEM] Standard ADB Interface initialized.")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    screenshot_path = os.path.join(script_dir, "vision", "live_screen.png")

    print(f"\n[SYSTEM] History loaded. Previous Solves: {logger.total_solves}")
    print("[READY] The bot is searching for targets...")
    time.sleep(2)

    try:
        while True:
            level_solved = False
            
            while not level_solved:
                start_time = time.time()
                
                io_controller.get_screenshot(screenshot_path)
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
                    print("[!] Solver returned no moves. Retrying...")
                    time.sleep(1)
                    continue
                    
                print(f"[SOLVER] Sequence locked: {len(winning_sequence)} taps.")
                io_controller.execute_sequence(winning_sequence)
                
                total_time = time.time() - start_time
                logger.log_run(total_time)
                
                print("[AUTO] Waiting for tiles to settle...")
                time.sleep(0.1)
                print("[VALIDATOR] Re-scanning for verification...")
            
            print("[AUTO] Animations finished. Proceeding to next level.")
            time.sleep(0)
            io_controller.tap_pixel(*CLAIM_BUTTON_POS)
            time.sleep(0)
            
    except KeyboardInterrupt:
        print("\n\n[SYSTEM] Kill switch activated. Shutting down hardware bridge...")
        if hasattr(io_controller, 'shutdown'):
            io_controller.shutdown()
        raise 

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_dir, "logs.txt")

    bot_logger = StatsLogger(log_file_path)
    
    try:
        run_bot(bot_logger)
    except KeyboardInterrupt:
        bot_logger.write_session_end()
        print("[SYSTEM] Session statistics written to logs.txt. Goodbye.")