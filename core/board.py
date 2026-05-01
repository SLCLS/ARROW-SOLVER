class ArrowBoard:
    def __init__(self):
        self.radius = 3
        self.tiles = {}
        self._initialize_board()

    def _initialize_board(self):

        for q in range(-self.radius, self.radius + 1):
            for r in range(-self.radius, self.radius + 1):
                if abs(q + r) <= self.radius:
                    self.tiles[(q, r)] = 1

    def get_neighbors(self, q, r):

        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]

        neighbors = []

        for dq, dr in directions:
            nq, nr = q + dq, r + dr

            if (nq, nr) in self.tiles:
                neighbors,append((nq, nr))
        
        return neighbors
    
    def tap(self, q, r):

        if (q, r) not in self.tiles:
            raise ValueError(f"Coordinates ({q}, {r}) out of bounds.")
        
        self._increment(q, r)

        for nq, nr in self.get_neighbors(q, r):
            self._increment(nq, nr)

    def _increment(self, q, r):

        self.tiles[(q, r)] = (self.tiles[(q, r)] % 6) + 1

    def set_state(self, state_dict):

        for coord, val in state_dict.items():
            if coord in self.tiles:
                if 1 <= val <= 6:
                    self.tiles[coord] = val
                else:
                    raise ValueError(f"Value must be 1-6, got {val} at {coord}.")
                
    def is_solved(self):

        return all(val == 1 for val in self.tiles.values())
    
    def print_board(self):

        print("\n--- Current Board State ---")

        for r in range(-self.radius, self.radius + 1):  
            row_str = ""
            offset = " " * abs(r)

            for q in range(-self.radius, self.radius + 1):
                if (q, r) in self.tiles:
                    row_str += f"{self.tiles[(q, r)]} "
            
            print(offset + row_str)
        print("---------------------------\n")

if __name__ == "__main__":
    board = ArrowBoard()
    board.print_board()
    
    print("Tapping (0, 0)...")
    board.tap(2, -1)
    board.print_board()