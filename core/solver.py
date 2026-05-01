import random
from board import ArrowBoard

class ArrowSolver:
    def __init__(self, board):
        self.board = board
        self.solution_taps = []

    def _tap(self, q, r, times):
        times = times % 6
        if times == 0:
            return
        for _ in range(times):
            self.board.tap(q, r)
            self.solution_taps.append((q, r))

    def propagate(self):
        for r in range(-3, 3):
            for q in range(-3, 4):
                if (q, r) in self.board.tiles:
                    val = self.board.tiles[(q, r)]
                    if val != 1:
                        taps_needed = (7 - val) % 6

                        if (q, r + 1) in self.board.tiles:
                            self._tap(q, r + 1, taps_needed)

    def execute_endgame(self):
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
        self.solution_taps.clear()
        
        self.propagate()
        self.execute_endgame()
        self.propagate()
        
        return self.solution_taps

if __name__ == "__main__":
    test_board = ArrowBoard()
    
    print("Scrambling board with 50 random taps...")

    valid_coords = list(test_board.tiles.keys())
    for _ in range(50):
        q, r = random.choice(valid_coords)
        test_board.tap(q, r)
        
    print("\n[Scrambled State]")
    test_board.print_board()
   
    solver = ArrowSolver(test_board)
    print("Executing solver algorithm...")
    solution = solver.solve()
    
    print("\n[Final State - Should be all 1s]")
    test_board.print_board()
    
    if test_board.is_solved():
        print(f"SUCCESS! Board solved in {len(solution)} total taps.")
        from collections import Counter
        tap_counts = Counter(solution)
        print("\nOptimal Batch Execution Sequence:")
        for coord, count in tap_counts.items():
            print(f"Tap {coord}: {count % 6} times")
    else:
        print("FAILED: Board is not solved.")