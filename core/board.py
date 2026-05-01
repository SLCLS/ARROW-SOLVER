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
                neighbors.append((nq, nr))
        return neighbors

    def tap(self, q, r):
        if (q, r) not in self.tiles:
            raise ValueError(f"Coordinate ({q}, {r}) is out of bounds.")

        self._increment(q, r)
 
        for nq, nr in self.get_neighbors(q, r):
            self._increment(nq, nr)

    def _increment(self, q, r):
        self.tiles[(q, r)] = (self.tiles[(q, r)] % 6) + 1

    def set_state(self, state_dict):
        """Injects a known board state."""
        for coord, val in state_dict.items():
            if coord in self.tiles:
                if 1 <= val <= 6:
                    self.tiles[coord] = val
                else:
                    raise ValueError(f"Tile value must be 1-6. Got {val}.")

    def is_solved(self):
        """Checks if all tiles are exactly 1."""
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
    
    print("Interactive Board Simulator (Mod 6)")
    print("Type coordinates as 'q,r' to tap a tile (e.g., '0,0').")
    print("Type 'exit' to quit.\n")
    
    while True:
        board.print_board()
        user_input = input("Enter coordinate to tap (q,r): ").strip()
        
        if user_input.lower() == 'exit':
            print("Exiting simulator...")
            break
            
        try:
            q_str, r_str = user_input.split(',')
            q, r = int(q_str.strip()), int(r_str.strip())
            
            board.tap(q, r)
            print(f"\n[+] Tapped ({q}, {r})")
            
        except ValueError as e:
            if "out of bounds" in str(e):
                print(f"\n[!] Error: {e}")
            else:
                print("\n[!] Invalid format. Please use 'q,r' (e.g., '1,-1')")
        except Exception as e:
            print(f"\n[!] Unexpected Error: {e}")