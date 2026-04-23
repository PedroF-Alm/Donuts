from core.slot import Slot
from core.ring import Ring
from core.graph import Graph
import random
import math
import copy

class Game:    
    
    PLAYER_ONE = 0
    PLAYER_TWO = 1

    def __init__(self, seed: int) -> None:
        random.seed(seed)

        self.grid: list[Slot] = []
        self.turn = Game.PLAYER_ONE
        self.winner = None
        self.end = False
        self.player_rings = [15, 15]
        self.states = []

        for i in range(0, 36):                  
            self.grid.append(Slot(random.randint(0, 3)))

    def get_xy(self, i: int) -> tuple[int, int]:
        if 0 <= i < 36:
            return (i % 6, i // 6)
        return None
    
    def get_me(self, x: int, y: int) -> int:
        if 0 <= x < 6 and 0 <= y < 6:
            return y * 6 + x
        return None

    def get_theta(self, x0: int, y0: int, x1: int, y1: int) -> int:
        if x0 == x1:
            return 90 if y1 > y0 else -90
        else:
            return int(math.degrees(math.atan((y1 - y0) / (x1 - x0))))

    def change_slots(self, x0: int, y0: int, direction: int):
        for i in range(0, 36):        

            if self.grid[i].ring != None:
                continue

            x = i % 6
            y = i // 6                 
            if x == x0 and y == y0:
                continue

            theta = self.get_theta(x0, y0, x, y)

            if direction == Slot.SECOND_DIAGONAL:                
                self.grid[i].blocked = theta != -45
            elif direction == Slot.FIRST_DIAGONAL:           
                self.grid[i].blocked = theta != 45
            elif direction == Slot.VERTICAL:            
                self.grid[i].blocked = abs(theta) != 90 
            elif direction == Slot.HORIZONTAL:            
                self.grid[i].blocked = theta != 0
      
        count = 0
        for s in self.grid:
            if s.blocked:
                count += 1
        if count == 36:
            for s in self.grid:
                if s.ring == None:
                    s.blocked = False

    
    def get_neighbors(self, x: int, y: int) -> list[list[Ring]]:
        
        second_diagonal = []
        first_diagonal = []
        vertical = []
        horizontal = []

        for i in range(0, 36):

            xi, yi = self.get_xy(i)

            if x == xi and y == yi:
                second_diagonal.append(self.grid[i].ring)
                first_diagonal.append(self.grid[i].ring)
                vertical.append(self.grid[i].ring)
                horizontal.append(self.grid[i].ring)
                continue

            theta = self.get_theta(x, y, xi, yi)
        
            if theta == -45:                
                second_diagonal.append(self.grid[i].ring)
            elif theta == 45:
                first_diagonal.append(self.grid[i].ring)
            elif abs(theta) == 90:
                vertical.append(self.grid[i].ring)
            elif theta == 0:
                horizontal.append(self.grid[i].ring)

        return [second_diagonal, first_diagonal, vertical, horizontal]

    def grab_donuts(self, x: int, y: int) -> None:

        neighbors = self.get_neighbors(x, y)

        myself = self.grid[self.get_me(x, y)].ring
                        
        for directed_neighbors in neighbors:                                        
            neighborhood_clusters = []
            cluster = []

            for n in directed_neighbors:
                if n is None:
                    if cluster:  # avoid empty chunks (like str.split)
                        neighborhood_clusters.append(cluster)
                        cluster = []
                else:
                    cluster.append(n)

            if cluster:
                neighborhood_clusters.append(cluster)

            for cluster in neighborhood_clusters:
                if len(cluster) < 3 or myself not in cluster:
                    continue

                middle = cluster.index(myself)

                edge1 = middle
                edge2 = middle

                while cluster[edge1].owner == cluster[middle].owner and edge1 > 0:
                    edge1 -= 1
                while cluster[edge2].owner == cluster[middle].owner and edge2 < len(cluster) - 1:
                    edge2 += 1

                edges = (cluster[edge1], cluster[edge2])                

                if edges[0].owner != edges[1].owner:
                    continue
                
                edges[0].owner = self.turn
                edges[1].owner = self.turn
                
    def is_sublist(self, sub: list, main: list):
        n = len(sub)
        return any(sub == main[i:i + n] for i in range(len(main) - n + 1))
    
    def get_owner(self, slt: Slot) -> int:
        if slt.ring is None:
            return -1
        else:
            return slt.ring.owner
    
    def get_owners(self, slots: list[Slot]) -> list[int]:
        return list(map(lambda slt: self.get_owner(slt), slots))

    def get_fives(self) -> bool:
        fives = [self.turn]*5
        result = False

        second_diagonal_middle = self.get_owners(self.grid[5::5])
        second_diagonal_top    = self.get_owners(self.grid[4::5])
        second_diagonal_bottom = self.get_owners(self.grid[11::5])

        first_diagonal_middle  = self.get_owners(self.grid[0::7])
        first_diagonal_top     = self.get_owners(self.grid[1::7])
        first_diagonal_bottom  = self.get_owners(self.grid[6::7])

        if self.is_sublist(fives, second_diagonal_middle):  
            for s in self.grid[5::5]:
                if s.ring is not None and s.ring.owner == self.turn:
                    s.marked = True   
            result = True         
        
        if fives == second_diagonal_top:
            for s in self.grid[4::5]:
                s.marked = True            
            result = True
        
        if fives == second_diagonal_bottom:
            for s in self.grid[11::5]:
                s.marked = True            
            result = True
        
        if self.is_sublist(fives, first_diagonal_middle):  
            for s in self.grid[0::7]:
                if s.ring is not None and s.ring.owner == self.turn:
                    s.marked = True            
            result = True
        
        if fives == first_diagonal_top:
            for s in self.grid[1::7]:
                s.marked = True
            result = True
        
        if fives == first_diagonal_bottom:
            for s in self.grid[6::7]:
                s.marked = True
            result = True        
        
        for i in range(0, 6):            
            horizontal = self.get_owners(self.grid[i*6:i*6+6])
            vertical   = self.get_owners(self.grid[i::6])        
            if horizontal is not None and self.is_sublist(fives, horizontal):
                for s in self.grid[i*6:i*6+6]:
                    if s.ring is not None and s.ring.owner == self.turn:
                        s.marked = True
                result = True
                horizontal = None
            if vertical is not None and self.is_sublist(fives, vertical):
                for s in self.grid[i::6]:
                    if s.ring is not None and s.ring.owner == self.turn:
                        s.marked = True
                result = True    
                vertical = None        
        
        return result
    
    def most_donuts(self):
        graph = Graph()
        grid_owners = self.get_owners(self.grid)
        for i in range(0, 36):
            top = i - 6 
            left = i - 1
            right = i + 1
            bottom = i + 6
            if top >= 0 and grid_owners[top] == grid_owners[i]:
                graph.addEdge(i, top)
            if left >= 0 and (left - 5) % 6 != 0 and grid_owners[left] == grid_owners[i]:
                graph.addEdge(i, left)
            if right < 36  and right % 6 != 0 and grid_owners[right] == grid_owners[i]:
                graph.addEdge(i, right)
            if bottom < 36 and grid_owners[bottom] == grid_owners[i]:
                graph.addEdge(i, bottom)
        
        max_component_player_one = []
        max_component_player_two = []

        for c in graph.getComponents():              
            r = self.grid[c[0]].ring
            if r is not None:
                if r.owner == self.PLAYER_ONE and len(c) > len(max_component_player_one):
                    max_component_player_one = c
                elif r.owner == self.PLAYER_TWO and len(c) > len(max_component_player_two):
                    max_component_player_two = c

        if len(max_component_player_one) == len(max_component_player_two):
            return None
        elif len(max_component_player_one) > len(max_component_player_two):
            max_component = max_component_player_one
        else:
            max_component = max_component_player_two        

        for c in max_component:
            self.grid[c].marked = True

        return self.grid[max_component[0]].ring.owner

    def check_winner(self) -> None: 
        for s in self.grid:
            s.marked = False 

        if (self.get_fives()):
            self.winner = self.turn
            print(f"PLAYER {'ONE' if self.winner == Game.PLAYER_ONE else 'TWO'} WON!")
            self.end = True
            return True        
        
        if self.player_rings == [0, 0]:
            self.winner = self.most_donuts()
            if self.winner is None:
                print("TIE!")  
            else:              
                print(f"PLAYER {'ONE' if self.winner == Game.PLAYER_ONE else 'TWO'} WON!")
            self.end = True
            return True
        
        return False                    

    def evaluate(self, x: int, y: int) -> None:    
        self.grab_donuts(x, y)        
        self.check_winner()

    def save_state(self):
        save = [copy.deepcopy(self.grid), self.player_rings.copy(), self.turn, self.end]
        self.states.append(save)
    
    def last_state(self) -> bool:        
        if self.states:
            state = self.states.pop()
            self.grid         = state[0]
            self.player_rings = state[1]
            self.turn         = state[2]
            self.end          = state[3]
            
            return True
        return False


    def place_ring(self, x: int, y: int) -> bool:        
        if not self.end and 0 <= x < 6 and 0 <= y < 6 and self.player_rings[self.turn] > 0:
            slot_2_place: Slot = self.grid[y * 6 + x]
            if slot_2_place.ring == None and not slot_2_place.blocked:
                self.save_state()
                slot_2_place.ring = Ring(self.turn)   
                slot_2_place.blocked = True                 
                self.player_rings[self.turn] -= 1
                self.evaluate(x, y)                    
                self.change_slots(x, y, slot_2_place.direction)                     
                self.turn = Game.PLAYER_TWO if self.turn == Game.PLAYER_ONE else Game.PLAYER_ONE                
                return True
            else:
                return False
        return False