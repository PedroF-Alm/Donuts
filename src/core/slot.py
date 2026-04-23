from core.ring import Ring

class Slot:

    SECOND_DIAGONAL = 0
    FIRST_DIAGONAL = 1
    VERTICAL = 2
    HORIZONTAL = 3

    def __init__(self, direction: int = 0) -> None:
        self.ring: Ring = None    
        self.direction = direction if 0 <= direction < 4 else 0       
        self.blocked = False        
        self.marked = False