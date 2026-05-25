from core.game import Game

def minimax(self, state: Game, i: int, parent_node: Node, depth: int, maximizingPlayer: bool):
        # Cria ou obtém o nó atual (referência no estado)
        current_node = Node(state.serialize_state(i))
        if parent_node is not None:
            parent_node.add_child(current_node)
        
        # Condição de parada
        if depth == 0 or state.end:
            return state.heuristic(state), [current_node]
        
        next_states = state.expand_next_states()
        if not next_states:
            return state.heuristic(state), [current_node]

        best_score = -float('inf') if maximizingPlayer else float('inf')
        best_path = []

        for next_game, move_i in next_states:
            # Para rastrear o nó correto, você precisa garantir que o 
            # state_tree_reference esteja atualizado na recursão
            score, path = self.minimax(next_game, move_i, current_node, depth - 1, not maximizingPlayer)
            
            if maximizingPlayer:
                if score > best_score:
                    best_score = score
                    best_path = [current_node] + path
            else:
                if score < best_score:
                    best_score = score
                    best_path = [current_node] + path
                    
        return best_score, best_path
    
    def heuristic(self, state: Game):
        if state.winner == Game.PLAYER_TWO:
            return 10000
        elif state.winner == Game.PLAYER_ONE:
            return -10000
        else:
            return 0

    def calculate_best_play(self, depth: int) -> int:  
        player = self.turn  
        best_score = -float('inf') if player == Game.PLAYER_TWO else float('inf')
        best_index = -1
        best_nodes_path = []

        next_states = self.expand_next_states()
        
        for next_game, i in next_states:
            # Chama o minimax
            score, path = self.minimax(next_game, i, self.state_tree_reference, depth - 1, player == Game.PLAYER_TWO)
            
            # Atualiza o melhor movimento global
            if player == Game.PLAYER_TWO: # Maximizing
                if score > best_score:
                    best_score = score
                    best_index = i
                    best_nodes_path = path
            else: # Minimizing
                if score < best_score:
                    best_score = score
                    best_index = i
                    best_nodes_path = path

        # Marca os nós do melhor caminho no XML
        for node in best_nodes_path:
            if node is not None:
                node.set_xml_attribute('best', 'True')
                
        return best_index

    def minimax(self, state: Game, i: int, parent_node: Node, depth = -1, alpha: float = -float('inf'), beta: float = float('inf'), maximizingPlayer: bool = True):
        current_node = Node(state.serialize_state(i))   
        if parent_node is not None:                                        
            parent_node.add_child(current_node)   

        if depth == 0 or state.end:
            return state.heuristic(state)
        
        next_states = state.expand_next_states()
        
        if not next_states:
            return self.heuristic(state)

        if maximizingPlayer:
            max_score = -float('inf')
            for next, i in next_states:
                score = state.minimax(next, i, current_node, depth - 1, maximizingPlayer=False)
                max_score = max(max_score, score)                
            return max_score            
        else:
            min_score = float('inf')
            for next, i in next_states:
                score = state.minimax(next, i, current_node, depth - 1, maximizingPlayer=True)
                min_score = min(min_score, score)                
            return min_score

    def heuristic(self, state: Game):
        if state.winner == Game.PLAYER_TWO:
            return 10000
        elif state.winner == Game.PLAYER_ONE:
            return -10000
        else:
            return 0
    
    def calculate_best_play(self, depth: int) -> int:  
        player = self.turn  
        best_score = -float('inf')
        best_index = -1        

        next_states = self.expand_next_states()
        
        for next, i in next_states:                                
            score = self.minimax(next, i, self.state_tree_reference, depth, maximizingPlayer=player == Game.PLAYER_TWO)            
            if score > best_score:
                best_score = score
                best_index = i
                
        return best_index


    def minimax(self, state: Game, i: int, parent_node: Node, depth = -1, alpha: float = -float('inf'), beta: float = float('inf'), maximizingPlayer: bool = True):
        current_node = Node(state.serialize_state(i))   
        if parent_node is not None:                                        
            parent_node.add_child(current_node)   

        if depth == 0 or state.end:
            return state.heuristic(state)
        
        next_states = state.expand_next_states()
        
        if not next_states:
            return self.heuristic(state)

        if maximizingPlayer:
            max_score = -float('inf')
            for next, i in next_states:
                score = state.minimax(next, i, current_node, depth - 1, maximizingPlayer=False)
                max_score = max(max_score, score)                
            return max_score            
        else:
            min_score = float('inf')
            for next, i in next_states:
                score = state.minimax(next, i, current_node, depth - 1, maximizingPlayer=True)
                min_score = min(min_score, score)                
            return min_score

    def heuristic(self, state: Game):
        if state.winner == Game.PLAYER_TWO:
            return 10000
        elif state.winner == Game.PLAYER_ONE:
            return -10000
        else:
            return 0
    
    def calculate_best_play(self, depth: int) -> int:  
        player = self.turn  
        best_score = -float('inf')
        best_index = -1        

        next_states = self.expand_next_states()
        
        for next, i in next_states:                                
            score = self.minimax(next, i, self.state_tree_reference, depth, maximizingPlayer=player == Game.PLAYER_TWO)            
            if score > best_score:
                best_score = score
                best_index = i
                
        return best_index