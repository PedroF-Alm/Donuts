import random
import numpy as np
import copy
from pathlib import Path
from core.game import Game

class Learner():

    def __init__(self, parameters: dict = {}):
        self.Q_TABLE = {}        
        self.parameters = {
            'SEED': 1,
            'LEARNING_RATE':    0.1,
            'DISCOUNT_FACTOR':  0.9,
            'INITIAL_EPSILON':  1.0,
            'EPSILON_MIN':      0.01,
            'EPSILON_DECAY':    0.99995,
            'VICTORY_REWARD':   10,
            'TIE_REWARD':       1,
            'DEFEAT_PENALTY':   -10
        }
        for p in parameters.keys():
            self.parameters[p] = parameters[p]        
        self.game: Game = None
    
    def get_q_values(self, q_table: dict, state: Game, q_player: int): 
        if q_player == Game.PLAYER_ONE:       
            key = f"{len(state.max_component_player_one)}"
            key += f":{len(state.max_component_player_two)}"
        else:
            key = f"{len(state.max_component_player_two)}"
            key += f":{len(state.max_component_player_one)}"
        key += f":{len(state.get_lines())}"
        lines = state.get_lines()        
        for line in lines:
            owners = state.get_owners(line)
            mm_rings = owners.count(Game.PLAYER_ONE if q_player == Game.PLAYER_TWO else Game.PLAYER_TWO)
            q_rings = owners.count(q_player)
            available = len(owners) - mm_rings - q_rings
            key += f":{q_rings}:{mm_rings}:{available}"
        blocked_count = sum([1 if state.grid[i].blocked else 0 for i in range(36)])
        key += f":{blocked_count}"
        key += f":{state.turn}"
        if key not in q_table:
            q_table[key] = np.zeros(36)
        return q_table[key]

    def choose_action(self, q_table: dict, state: Game, epsilon, q_player: int):        
        q_values = self.get_q_values(q_table, state, q_player)

        valid_moves = state.get_valid_moves()

        # EXPLORATION
        if random.uniform(0, 1) < epsilon:
            return random.choice(valid_moves)

        # EXPLOITATION                
        best_action = max(valid_moves, key=lambda a: q_values[a])

        return best_action     
    
    # ==========================================  
    # Q-LEARNING
    # ==========================================  

    def learn(self, q_table, state, action, reward, next_state, q_player):
        q_values      = self.get_q_values(q_table, state, q_player)
        q_next_values = self.get_q_values(q_table, next_state, q_player)
        old_value = q_values[action]

        future_best = np.max(q_next_values)     

        new_value = old_value + self.parameters['LEARNING_RATE'] * (reward + self.parameters['DISCOUNT_FACTOR'] * future_best - old_value)

        q_values[action] = new_value

    def train(self, rounds: int):

        epsilon = self.parameters['INITIAL_EPSILON']      
        script_dir = Path(__file__).resolve().parent          
    
        mm_depth = 2
        random_play = 0.5        

        for r in range(rounds):             

            try:
                self.game: Game = Game(seed=r)            
                game = self.game                    
                
                q_player = random.choice([Game.PLAYER_ONE, Game.PLAYER_TWO])   
                mm_player = Game.PLAYER_ONE if q_player == Game.PLAYER_TWO else Game.PLAYER_TWO                

                if game.turn == mm_player:                        
                    x, y = game.get_xy(game.calculate_best_play(mm_player, mm_depth, True))
                    game.place_ring(x, y)                 

                while not game.end:                        

                    state = copy.deepcopy(game)

                    valid_moves = game.get_valid_moves()
                    if valid_moves == []:
                        break

                    # Learner
                    action = self.choose_action(self.Q_TABLE, state, epsilon, q_player)                    
                    x, y = game.get_xy(action)
                    game.place_ring(x, y)                        
                
                    if game.end:    
                        next_state = copy.deepcopy(game)
                        reward = self.calculate_reward(q_player, state, next_state)
                        self.learn(self.Q_TABLE, state, action, reward, next_state, q_player)                                                 
                        break
                    
                    # Opponent                           
                    use_mm = random.random() < random_play                                  
                    x, y = game.get_xy(game.calculate_best_play(mm_player, mm_depth, True) if use_mm else random.choice(game.get_valid_moves()))                     

                    game.place_ring(x, y)     

                    next_state = copy.deepcopy(game)

                    reward = self.calculate_reward(q_player, state, next_state)
                    self.learn(self.Q_TABLE, state, action, reward, next_state, q_player)  

                    if game.end:                        
                        break     
                        
                victory_log = open(f'{script_dir}/victory.csv', 'a') 
                if game.winner == q_player:
                    victory_log.write('1,')                       
                elif game.winner == mm_player:
                    victory_log.write('-1,')
                else:
                    victory_log.write('0,')                        
                victory_log.close()

                if r % 1000 == 0:
                    self.save_q_table()
                    print(f"Saved q_tables on round {r}")

                epsilon = max(self.parameters['EPSILON_MIN'], self.parameters['INITIAL_EPSILON'] - (self.parameters['INITIAL_EPSILON']-self.parameters['EPSILON_MIN']) * (r / rounds))
            except Exception as e:
                print(f"Training stopped on round {r}")                          
                print(e)                          

    def save_q_table(self, dir: str = '.'):
        script_dir = Path(__file__).resolve().parent
        with open(f'{script_dir}/{dir}/q_table.csv', 'w') as file:
            for k in self.Q_TABLE.keys():
                file.write(k + ",")
                for i in range(len(self.Q_TABLE[k])):
                    v = str(self.Q_TABLE[k][i])
                    file.write(v + ("," if i < len(self.Q_TABLE[k]) - 1 else ''))
                file.write('\n')

    def load_q_table(self, dir: str = '.'):
        script_dir = Path(__file__).resolve().parent
        try:                
            with open(f'{script_dir}/{dir}/q_table.csv', 'r') as file:
                lines = file.readlines()            
                for l in lines:
                    l = l.strip().split(',')
                    self.Q_TABLE[l[0]] = np.zeros(36)
                    for i in range(36):                    
                        self.Q_TABLE[l[0]][i] = float(l[i+1])    
        except FileNotFoundError:
            self.save_q_table()

    def calculate_reward(self, favorite: int, state: Game, next_state: Game) -> float:
        
        reward = 0

        if favorite == Game.PLAYER_ONE:
            reward = (len(next_state.max_component_player_one) - len(state.max_component_player_one)) * 3
        elif favorite == Game.PLAYER_TWO:
            reward = (len(next_state.max_component_player_two) - len(state.max_component_player_two)) * 3

        state_lines = state.get_lines()
        next_state_lines = next_state.get_lines()        

        for i in range(len(state_lines)):
            score_sl  = state.line_score(favorite, state.get_owners(state_lines[i]))
            score_nsl = next_state.line_score(favorite, next_state.get_owners(next_state_lines[i]))
            reward += 0.05 * (score_nsl - score_sl)

        if next_state.winner == favorite:
            reward += self.parameters['VICTORY_REWARD']
        elif next_state.winner is None and next_state.end:
            reward += self.parameters['TIE_REWARD']
        elif next_state.end:
            reward += self.parameters['DEFEAT_PENALTY']

        return reward
