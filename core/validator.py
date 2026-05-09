def is_board_solved(board_state):
    if not board_state:
        return False
    
    for coord, val in board_state.items():
        if val != 1:
            return False
        
    return True