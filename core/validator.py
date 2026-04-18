def is_board_solved(board_state):
    """Returns True if every tile in the state is 1."""
    if not board_state:
        return False
        
    for coord, val in board_state.items():
        if val != 1:
            return False
    return True