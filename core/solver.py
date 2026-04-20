import random
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
        Sweeps the board from top to bottom.
        Uses the down-right neighbor (q, r+1) to fix the tile (q, r).
        """
        if self.verbose:
            print("\n>>> STARTING PROPAGATION SWEEP <<<")
            
        for r in range(-3, 3):
            for q in range(-3, 4):
                if (q, r) in self.board.tiles:
                    val = self.board.tiles[(q, r)]
                    if val != 1:
                        taps_needed = (7 - val) % 6
                        if (q, r + 1) in self.board.tiles:
                            self._tap(q, r + 1, taps_needed)

    def execute_endgame(self):
        """Executes the parity alignment logic."""
        if self.verbose:
            print("\n>>> STARTING ENDGAME SEQUENCE <<<")
            
        A, B, C, D = (0, 3), (1, 2), (2, 1), (3, 0)
        a, b, c, d = (0, -3), (1, -3), (2, -3), (3, -3)

        val_C = self.board.tiles[C]
        val_a = self.board.tiles[a]
        taps_for_a = (val_C - val_a) % 6
        self._tap(*a, taps_for_a)

        taps_to_solve_C = (7 - self.board.tiles[C]) % 6
        self._tap(*b, taps_to_solve_C)
        self._tap(*d, taps_to_solve_C)

        taps_to_solve_D = (7 - self.board.tiles[D]) % 6
        self._tap(*a, taps_to_solve_D)

        val_B = self.board.tiles[B]
        val_D = self.board.tiles[D]
        if (val_B + val_D) % 2 != 0:
            self._tap(*c, 3)

    def solve(self):
        """Master sequence returning an absolutely minimal physical execution array."""
        self.tap_map.clear()
        
        self.propagate()
        self.execute_endgame()
        self.propagate()
        
        optimized_sequence = []
        for coord, count in self.tap_map.items():
            if count > 0:
                optimized_sequence.extend([coord] * count)
                
        return optimized_sequence

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
    solution = solver.solve()
    
    print("\n========================================")
    print("       [FINAL STATE & STATISTICS]       ")
    print("========================================")
    test_board.print_board()
    
    if test_board.is_solved():
        print(f"SUCCESS! Board solved in exactly {len(solution)} optimized physical taps.")
    else:
        print("FAILED: Board is not solved.")