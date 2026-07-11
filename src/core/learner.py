import random
import numpy as np
from pathlib import Path
from core.game import Game
import csv

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
            'VICTORY_REWARD':   100,      
            'TIE_REWARD':       10,
            'DEFEAT_PENALTY':   -100
        }
        for p in parameters.keys():
            self.parameters[p] = parameters[p]        
        self.game: Game = None

    def get_q_values(self, q_table: dict, state: Game, q_player: int):       
        if state.last_play is not None: 
            x, y = state.get_xy(state.last_play)
            interceptors = list(state.get_interceptors(x, y))            

            if hasattr(state.grid[0], 'owner'):                
                for i in range(len(interceptors)):                    
                    interceptors[i] = ''.join(['3' if state.grid[j].owner == -1 and state.grid[j].blocked else (str(1 if state.grid[j].owner == q_player else 0) if state.grid[j].owner != -1 else '2') for j in interceptors[i]])
            else:                
                for i in range(len(interceptors)):                    
                    interceptors[i] = ''.join(['3' if state.get_owner(state.grid[j]) == -1 and state.grid[j].blocked else (str(1 if state.get_owner(state.grid[j]) == q_player else 0) if state.get_owner(state.grid[j]) != -1 else '2') for j in interceptors[i]])
        else:
            interceptors = "SSSS"

        H = min(interceptors[0], interceptors[0][::-1])
        V = min(interceptors[1], interceptors[1][::-1])
        F = min(interceptors[2], interceptors[2][::-1])
        S = min(interceptors[3], interceptors[3][::-1])

        key = f'H({H}):V({V}):F({F}):S({S})'

        if key not in q_table:
            q_table[key] = np.zeros(36, dtype=np.float32)

        return q_table[key]

    def choose_action(self, q_table: dict, state: Game, epsilon, q_player: int):        
        q_values = self.get_q_values(q_table, state, q_player)
        valid_moves = state.get_valid_moves()

        if not valid_moves:
            return None

        # EXPLORATION
        if random.uniform(0, 1) < epsilon:
            return random.choice(valid_moves)

        # EXPLOITATION                
        best = np.max(q_values[valid_moves])        
        best_actions = [a for a in valid_moves if q_values[a] == best]        
        return random.choice(best_actions)

    def learn(self, q_table, state, action, reward, next_state, q_player):
        q_values      = self.get_q_values(q_table, state, q_player)
        q_next_values = self.get_q_values(q_table, next_state, q_player)
        old_value = q_values[action]
          
        valid = next_state.get_valid_moves()
        if valid:
            future_best = np.max(q_next_values[valid])
        else:
            future_best = 0

        new_value = old_value + self.parameters['LEARNING_RATE'] * (reward + self.parameters['DISCOUNT_FACTOR'] * future_best - old_value)
        q_values[action] = new_value

    def train(self, rounds: int):
        epsilon = self.parameters['INITIAL_EPSILON']      
        script_dir = Path(__file__).resolve().parent            

        for r in range(rounds):                        
            self.game = Game(seed=self.parameters['SEED'])
            game = self.game                    
            random.seed(r)           

            agent_player = Game.PLAYER_ONE if random.randint(0, 1) else Game.PLAYER_TWO
            
            prob = random.uniform(0, 1)

            if prob < 0.50:
                opponent = 0
            elif prob < 0.75:
                opponent = 1
            elif prob < 1:
                opponent = 2
                        
            history = []    

            if agent_player == Game.PLAYER_TWO:
                if opponent:
                    position = game.calculate_best_play(opponent, True)
                else:
                    position = random.choice(game.get_valid_moves())
                x, y = game.get_xy(position)
                game.place_ring(x, y)                    

            while not game.end:                        
                past_state = game.clone()

                # 1. Agent moves
                action = self.choose_action(self.Q_TABLE, past_state, epsilon, agent_player)                    
                if action is None:
                    break
                x, y = game.get_xy(action)
                game.place_ring(x, y)

                next_state = game.clone()

                if game.end:
                    history.append((past_state, action, next_state))                    
                    for (state, action, next) in reversed(history):                            
                        reward = self.calculate_reward(agent_player, state, next) 
                        self.learn(self.Q_TABLE, state, action, reward, next, agent_player)                        
                    break

                # 2. Opponent moves
                if opponent:
                    position = game.calculate_best_play(opponent, True)
                else:
                    position = random.choice(game.get_valid_moves())
                x, y = game.get_xy(position)
                game.place_ring(x, y)
                
                # Capture board state immediately after agent's specific move
                next_state = game.clone()

                history.append((past_state, action, next_state))                

                if game.end:                    
                    for (state, action, next) in reversed(history):                            
                        reward = self.calculate_reward(agent_player, state, next) 
                        self.learn(self.Q_TABLE, state, action, reward, next, agent_player)                        
                    break

            # Log step metrics safely
            with open(f"{script_dir}/victory{opponent}.csv", "a") as victory_log:               
                if game.winner == agent_player:
                    victory_log.write('1,') 
                elif game.winner is None:  
                    victory_log.write('0,')                
                else:
                    victory_log.write('-1,')   
            with open(f"{script_dir}/victory.csv", "a") as victory_log:               
                if game.winner == agent_player:
                    victory_log.write('1,') 
                elif game.winner is None:  
                    victory_log.write('0,')                
                else:
                    victory_log.write('-1,')                       

            if r % 1000 == 0 and r > 0:
                self.save_q_table()
                print(f"Saved q_table on round {r}. Table row count: {len(self.Q_TABLE)}")

            epsilon = max(self.parameters['EPSILON_MIN'], epsilon * self.parameters['EPSILON_DECAY'])         

    def save_q_table(self, dir: str = '.'):
        script_dir = Path(__file__).resolve().parent        
        with open(f'{script_dir}/{dir}/q_table.csv', "w", newline="") as f:
            writer = csv.writer(f)
            for key, values in self.Q_TABLE.items():
                writer.writerow([key] + values.tolist())

    def load_q_table(self, dir: str = '.'):
        script_dir = Path(__file__).resolve().parent
        try:                
            with open(f'{script_dir}/{dir}/q_table.csv') as f:
                reader = csv.reader(f)
                for row in reader:
                    key = row[0]
                    self.Q_TABLE[key] = np.array(row[1:], dtype=np.float32)
        except FileNotFoundError:
            self.save_q_table()            

    def calculate_reward(self, favorite: int, state: Game, next_state: Game) -> float:
        reward = 0
        
        my_before = sum(1 for s in state.grid if s.owner == favorite)
        my_after = sum(1 for s in next_state.grid if s.owner == favorite)
        reward += 5 * (my_after - my_before)

        if next_state.winner == favorite:
            reward += self.parameters['VICTORY_REWARD']
        elif next_state.winner is None and next_state.end:
            reward += self.parameters['TIE_REWARD']
        elif next_state.end:
            reward += self.parameters['DEFEAT_PENALTY']

        return reward