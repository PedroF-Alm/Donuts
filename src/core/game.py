from core.slot import Slot
from core.ring import Ring
from core.graph import Graph
from util.tree import Node
import random
import math
import copy

class Game:    
    
    PLAYER_ONE = 0
    PLAYER_TWO = 1

    def __init__(self, seed: int, xml_file_name: str = None) -> None:
        random.seed(seed)

        self.grid: list[Slot] = []        
        self.turn = Game.PLAYER_ONE
        self.winner = None
        self.end = False
        self.step = 0
        self.player_rings = [15, 15]
        self.states = []
        self.state_tree = Node(None)
        self.state_tree_reference = self.state_tree
                
        self.max_component_player_one = []
        self.max_component_player_two = []
        self.placed_rings = [[0] * 18 for _ in range(2)] 
        self.last_move = None
        self.donuts_taken = 0
        
        for i in range(0, 36):                  
            self.grid.append(Slot(random.randint(0, 3)))

        if xml_file_name is not None:
            self.state_tree.load_from_xml(xml_file_name)
            self.xml_file_name = xml_file_name    
            self.save_tree_xml()        
        
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

        self.donuts_taken = 0
                        
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

                self.donuts_taken += 1
    
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
        target = [self.turn] * 5
        result = False
        
        lines = []

        for i in range(6):
            lines.append(self.grid[i*6 : i*6+6]) 
            lines.append(self.grid[i :: 6])      
        
        lines.append(self.grid[5:31:5]) 
        lines.append(self.grid[4:25:5]) 
        lines.append(self.grid[11:32:5])
        lines.append(self.grid[0:35:7]) 
        lines.append(self.grid[1:30:7]) 
        lines.append(self.grid[6:35:7])         
        
        self.placed_rings = [[0] * len(lines) for _ in range(2)] 

        for i in range(len(lines)):
            owners = self.get_owners(lines[i])            
            for o in owners:
                if o == Game.PLAYER_ONE or o == Game.PLAYER_TWO:
                    self.placed_rings[o][i] += 1            
            if self.is_sublist(target, owners): 
                for s in lines[i]:
                    if s.ring and s.ring.owner == self.turn:
                        s.marked = True
                result = True                
        
        return result
    
    def most_donuts(self) -> int | None:
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
        
        self.max_component_player_one = []
        self.max_component_player_two = []

        for c in graph.getComponents():              
            r = self.grid[c[0]].ring
            if r is not None:
                if r.owner == self.PLAYER_ONE and len(c) > len(self.max_component_player_one):
                    self.max_component_player_one = c
                elif r.owner == self.PLAYER_TWO and len(c) > len(self.max_component_player_two):
                    self.max_component_player_two = c

        if len(self.max_component_player_one) == len(self.max_component_player_two):            
            return None, None
        elif len(self.max_component_player_one) > len(self.max_component_player_two):
            max_component = self.max_component_player_one
        else:
            max_component = self.max_component_player_two     

        owner = self.grid[max_component[0]].ring.owner

        return max_component, owner

    def check_winner(self) -> None: 
        for s in self.grid:
            s.marked = False 

        if (self.get_fives()):
            self.winner = self.turn            
            self.end = True
            return True        
                
        max_c, owner = self.most_donuts()
        if self.player_rings == [0, 0]:
            if max_c is not None:
                for c in max_c:
                    self.grid[c].marked = True                
            self.winner = owner
            self.end = True
            return True
        
        return False                    

    def evaluate(self, x: int, y: int) -> None:    
        me = self.get_me(x, y)
        self.grid[me].ring = Ring(self.turn)            
        self.grid[me].blocked = True  
        self.player_rings[self.turn] -= 1
        self.grab_donuts(x, y)        
        self.check_winner()    
        self.change_slots(x, y, self.grid[me].direction)  
        self.step += 1

        child = Node(self.serialize_state()) 
        child.move = self.get_me(x, y)
        child.heuristic_p1 = self.heuristic(Game.PLAYER_ONE)
        child.heuristic_p2 = self.heuristic(Game.PLAYER_TWO)

        self.state_tree_reference = self.state_tree_reference.add_child(child)    
        
        self.turn = Game.PLAYER_TWO if self.turn == Game.PLAYER_ONE else Game.PLAYER_ONE

    def save_state(self) -> dict:
        state = {
            'grid': copy.deepcopy(self.grid), 
            'player_rings': self.player_rings.copy(), 
            'turn': self.turn, 
            'end': self.end, 
            'winner': self.winner, 
            'step': self.step,
            'tree_reference': self.state_tree_reference,       
            'max_c_p1': self.max_component_player_one,
            'max_c_p2': self.max_component_player_two,
            'last_move': self.last_move
        }

        self.states.append(state)
    
    def last_state(self) -> bool:        
        if self.states:
            state = self.states.pop()
            
            self.grid                     = state['grid']
            self.player_rings             = state['player_rings']
            self.turn                     = state['turn']
            self.end                      = state['end']
            self.winner                   = state['winner']
            self.step                     = state['step']            
            self.max_component_player_one = state['max_c_p1']
            self.max_component_player_two = state['max_c_p2']
            self.last_move                = state['last_move']            

            self.state_tree_reference = state['tree_reference']   
            
            return True
        return False
    
    def serialize_state(self) -> str:        
        owners = self.get_owners(self.grid)        
        return f"{owners}:{self.player_rings}:{self.turn}:{self.end}:{self.winner}:{self.step}"

    def get_valid_moves(self) -> list:      
        return [i for i in range(36) if not self.grid[i].blocked and self.grid[i].ring is None]

    def place_ring(self, x: int, y: int) -> bool:        
        if not self.end and 0 <= x < 6 and 0 <= y < 6 and self.player_rings[self.turn] > 0:

            slot_2_place: Slot = self.grid[y * 6 + x]

            if slot_2_place.ring == None and not slot_2_place.blocked:
                self.save_state()

                self.evaluate(x, y)                                    
                self.last_move = y * 6 + x

                return True
            else:
                return False
            
        return False
    
    def save_tree_xml(self):        
        if self.xml_file_name is not None:
            self.state_tree.save_to_xml(self.xml_file_name, active_node=self.state_tree_reference)

    def minimax(self, depth: int = -1, maximizingPlayer: bool = True, favorite = PLAYER_ONE) -> int:        
        valid_moves = self.get_valid_moves()
        if depth == 0 or self.end or not valid_moves:     
            serial = self.serialize_state().split(':')
            serial[2] = str(Game.PLAYER_ONE) if int(serial[2]) == Game.PLAYER_TWO else str(Game.PLAYER_ONE)
            serial = ':'.join(serial)
            known_state: Node = self.state_tree.node_index.get(serial)                
            if known_state is not None:     
                if favorite == Game.PLAYER_ONE:                           
                    return known_state.heuristic_p1
                else:
                    return known_state.heuristic_p2
            return self.heuristic(favorite)    

        best_score = -float('inf') if maximizingPlayer else float('inf')
        
        for move in valid_moves:              
            
            x, y = self.get_xy(move)

            if self.place_ring(x, y):            

                score = self.minimax(depth - 1, not maximizingPlayer, favorite)

                self.last_state()

                if maximizingPlayer:
                    if score > best_score:
                        best_score = score
                else:
                    if score < best_score:
                        best_score = score
                        
        return best_score
    
    def minimax_alpha_beta(self, depth: int = -1, alpha: float = -float('inf'), beta: float = float('inf'), maximizingPlayer: bool = True, favorite = PLAYER_ONE) -> int:        
        valid_moves = self.get_valid_moves()
        if depth == 0 or self.end or not valid_moves:
            serial = self.serialize_state().split(':')
            serial[2] = str(Game.PLAYER_ONE) if int(serial[2]) == Game.PLAYER_TWO else str(Game.PLAYER_ONE)
            serial = ':'.join(serial)
            known_state: Node = self.state_tree.node_index.get(serial)    
            if known_state is not None:                          
                if favorite == Game.PLAYER_ONE:                           
                    return known_state.heuristic_p1
                else:
                    return known_state.heuristic_p2
            return self.heuristic(favorite)

        best_score = -float('inf') if maximizingPlayer else float('inf')
        
        for move in valid_moves:             
            x, y = self.get_xy(move)

            if self.place_ring(x, y):
                
                score = self.minimax_alpha_beta(depth - 1, alpha, beta, not maximizingPlayer, favorite)

                self.last_state()

                if maximizingPlayer:
                    if score > best_score:
                        best_score = score
                    
                    alpha = max(alpha, best_score)
                    if beta <= alpha:
                        break  
                else:
                    if score < best_score:
                        best_score = score
                    
                    beta = min(beta, best_score)
                    if beta <= alpha:
                        break  
                        
        return best_score

    def heuristic(self, favorite) -> int:
        h = (len(self.max_component_player_one) - len(self.max_component_player_two)) * 3
        if favorite == Game.PLAYER_TWO:
            h = -h

        for i in range(0, 6):
            if self.last_move in range(i*6, i*6 + 6):
                if favorite == Game.PLAYER_ONE:
                    h -= self.placed_rings[1][i] 
                    h += self.placed_rings[0][i] * 2
                else:
                    h -= self.placed_rings[0][i] 
                    h += self.placed_rings[1][i] * 2
            if self.last_move in range(i, 36, 6):
                if favorite == Game.PLAYER_ONE:
                    h -= self.placed_rings[1][i + 1] 
                    h += self.placed_rings[0][i + 1] * 2
                else:
                    h -= self.placed_rings[0][i + 1]
                    h += self.placed_rings[1][i + 1] * 2

        ranges = [range(5, 31, 5), range(4, 25, 5), range(11, 32, 5), range(0, 35, 7), range(1, 30, 7), range(6, 35, 7)]        

        i = 12

        for r in ranges:
            if self.last_move in r:
                if favorite == Game.PLAYER_ONE:
                    h -= self.placed_rings[1][i] * 2
                    h += self.placed_rings[0][i]
                else:
                    h -= self.placed_rings[0][i] * 2
                    h += self.placed_rings[1][i] 
            i += 1

        h += self.donuts_taken * 10 * (1 if self.turn == favorite else -1)

        if self.winner == favorite:
            h += 1000
        elif self.winner is not None:
            h -= 1000   

        return h 

    def calculate_best_play(self, favorite, depth: int = 1, use_alpha_beta: bool = False) -> int:  
        player = self.turn  
        best_score = -float('inf')
        best_index = -1

        valid_moves = self.get_valid_moves()        
                
        for move in valid_moves:            

            x, y = self.get_xy(move)
            
            if self.place_ring(x, y):

                if use_alpha_beta:
                    score = self.minimax_alpha_beta(depth - 1, maximizingPlayer=player == favorite, favorite=favorite) 
                else:
                    score = self.minimax(depth - 1, player == favorite, favorite) 

                self.last_state()                     
                
                if score > best_score:
                    best_score = score
                    best_index = move

        return best_index