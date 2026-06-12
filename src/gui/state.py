from core.slot import Slot

class State:    
    
    PLAYER_ONE = 0
    PLAYER_TWO = 1

    def __init__(self) -> None:        
        self.grid: list[Slot]
        self.turn = State.PLAYER_ONE
        self.winner = None
        self.end = False        
        self.player_rings = [15, 15]         