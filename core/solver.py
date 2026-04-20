import random
import itertools
import time
from core.board import ArrowBoard

class ArrowSolver:
    def __init__(self, board, verbose=False):
        self.board = board
        self.tap_map = {} 
        self.verbose = verbose

    def _tap(self, q, r, times):
        """Executes taps internally and collapses redundant moves modulo 6."""
        if times == 0:
            return

        current_taps = self.tap_map.get((q, r), 0)
        self.tap_map[(q, r)] = (current_taps + times) % 6

        for _ in range(times):
            self.board.tap(q, r)

        if self.verbose:
            print(f"\n[INTERNAL] Tapped ({q}, {r}) {times} times.")
            self.board.print_board()

    def propagate(self):
        """
        Sweeps the board downward. 
        Forces the row below to fix the row above it.
        """
        for r in range(-3, 3):
            for q in range(-3, 4):
                if (q, r) in self.board.tiles:
                    val = self.board.tiles[(q, r)]
                    if val != 1:
                        taps_needed = (7 - val) % 6
                        if (q, r + 1) in self.board.tiles:
                            self._tap(q, r + 1, taps_needed)

    def solve(self):
        """
        Exhaustive Null Space Traversal.
        Simulates all states of the top edge to find the shortest physical execution path.
        """
        initial_tiles = self.board.tiles.copy()
        
        best_sequence = []
        min_taps = float('inf')
        best_top_taps = None
        
        top_row = [(0, -3), (1, -3), (2, -3), (3, -3)]
        
        original_verbose = self.verbose
        self.verbose = False
        
        for top_taps in itertools.product(range(6), repeat=4):
            self.board.tiles = initial_tiles.copy()
            self.tap_map.clear()
            
            for i, coord in enumerate(top_row):
                self._tap(*coord, top_taps[i])
                
            self.propagate()
            
            if all(val == 1 for val in self.board.tiles.values()):
                current_cost = sum(self.tap_map.values())
                if current_cost < min_taps:
                    min_taps = current_cost
                    best_top_taps = top_taps

        if best_top_taps is None:
            if self.verbose:
                print("[!] Mathematical Anomaly: Null Space traversal failed. Unsolvable board state.")
            return []
                    
        self.verbose = original_verbose
        if self.verbose:
            print(f"\n>>> OPTIMAL GENERATOR FOUND: {best_top_taps} <<<")
            
        self.board.tiles = initial_tiles.copy()
        self.tap_map.clear()
        
        for i, coord in enumerate(top_row):
            self._tap(*coord, best_top_taps[i])
            
        self.propagate()
        
        for coord, count in self.tap_map.items():
            if count > 0:
                best_sequence.extend([coord] * count)
                
        return best_sequence

if __name__ == "__main__":
    test_board = ArrowBoard()

    print("Scrambling board with 10 random taps...")
    valid_coords = list(test_board.tiles.keys())
    for _ in range(10):
        q, r = random.choice(valid_coords)
        test_board.tap(q, r)
        
    print("\n========================================")
    print("        [INITIAL SCRAMBLED STATE]       ")
    print("========================================")
    test_board.print_board()
    
    solver = ArrowSolver(test_board, verbose=False)
    
    math_start = time.perf_counter()
    solution = solver.solve()
    math_end = time.perf_counter()
    
    print("\n========================================")
    print("       [FINAL STATE & STATISTICS]       ")
    print("========================================")
    test_board.print_board()
    
    if test_board.is_solved():
        print(f"SUCCESS! Board solved.")
        print(f"Physical Taps Required: {len(solution)}")
        print(f"Mathematical CPU Calculation Time: {(math_end - math_start):.4f} seconds.")
    else:
        print("FAILED: Board is not solved.")