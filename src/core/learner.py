import random
import numpy as np
from pathlib import Path
from core.game import Game
import csv

class Learner():

    def __init__(self, parameters: dict = {}):
        self.Q_TABLE_P1 = {}
        self.Q_TABLE_P2 = {}
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
        if hasattr(state.grid[0], 'owner'):
            owners = [s.owner for s in state.grid]
        else:
            owners = state.get_owners(state.grid)            

        my_max_comp = len(state.max_component_p1 if q_player == Game.PLAYER_ONE else state.max_component_p2)
        opp_max_comp = len(state.max_component_p2 if q_player == Game.PLAYER_ONE else state.max_component_p1)
            
        comp_diff = "W" if my_max_comp > opp_max_comp else ("L" if my_max_comp < opp_max_comp else "E")
            
        threats = 0
        for line in state.get_lines():
            if hasattr(line[0], 'owner'):
                l_owners = [s.owner for s in line]
            else:
                l_owners = state.get_owners(line)             
            my_rings = l_owners.count(q_player)
            opp_rings = len(line) - my_rings - l_owners.count(-1)
            threats += 1 if opp_rings > my_rings else 0

        center_slots = [14, 15, 20, 21] 
        center_map = "".join(["1" if owners[c] == q_player else ("2" if owners[c] == -1 else "0") for c in center_slots])

        key = f'{comp_diff}:{threats}:{center_map}'

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

            agent_player = Game.PLAYER_ONE 
            opponent_player = Game.PLAYER_TWO
                        
            opponent_action = None
            after_opponent_state = None

            while not game.end:                        
                before_agent_state = game.clone()
                valid_moves = game.get_valid_moves()
                if not valid_moves:
                    break

                # 1. Agent moves
                action = self.choose_action(self.Q_TABLE_P1, before_agent_state, epsilon, agent_player)                    
                if action is None:
                    break
                x, y = game.get_xy(action)
                game.place_ring(x, y)                        
                
                # Capture board state immediately after agent's specific move
                after_agent_state = game.clone()

                if opponent_action is not None:
                    reward = self.calculate_reward(opponent_player, after_opponent_state, after_agent_state)
                    self.learn(self.Q_TABLE_P2, after_opponent_state, opponent_action, reward, after_agent_state, opponent_player)
                
                if game.end:    
                    reward = self.calculate_reward(agent_player, before_agent_state, after_agent_state)
                    self.learn(self.Q_TABLE_P1, before_agent_state, action, reward, after_agent_state, agent_player)                                                                        
                    break
                        
                # 2. Opponent moves
                opponent_action = self.choose_action(self.Q_TABLE_P2, after_agent_state, epsilon, opponent_player)                    
                if opponent_action is None:
                    break
                x, y = game.get_xy(opponent_action)
                game.place_ring(x, y) 

                after_opponent_state = game.clone()

                # 3. Evaluate the step based strictly on the player's performance impact
                # and pass the opponent's result as the next true state representation
                reward = self.calculate_reward(agent_player, before_agent_state, after_opponent_state)
                self.learn(self.Q_TABLE_P1, before_agent_state, action, reward, after_opponent_state, agent_player)  

                if game.end:    
                    reward = self.calculate_reward(opponent_player, after_agent_state, after_opponent_state)
                    self.learn(self.Q_TABLE_P2, after_agent_state, opponent_action, reward, after_opponent_state, opponent_player)                                                                        
                    break

            # Log step metrics safely
            with open(f"{script_dir}/victory.csv", "a") as victory_log:               
                if game.winner == agent_player:
                    victory_log.write('1,') 
                elif game.winner is None:  
                    victory_log.write('0,')                
                else:
                    victory_log.write('-1,')                        

            if r % 1000 == 0 and r > 0:
                self.save_q_tables()
                print(f"Saved q_tables on round {r}. Tables row count: {len(self.Q_TABLE_P1)}, {len(self.Q_TABLE_P2)}")

            epsilon = max(self.parameters['EPSILON_MIN'], self.parameters['INITIAL_EPSILON'] - (self.parameters['INITIAL_EPSILON']-self.parameters['EPSILON_MIN']) * (r / rounds))         

    def save_q_tables(self, dir: str = '.'):
        script_dir = Path(__file__).resolve().parent        
        with open(f'{script_dir}/{dir}/q_table_p1.csv', "w", newline="") as f:
            writer = csv.writer(f)
            for key, values in self.Q_TABLE_P1.items():
                writer.writerow([key] + values.tolist())
        with open(f'{script_dir}/{dir}/q_table_p2.csv', "w", newline="") as f:
            writer = csv.writer(f)
            for key, values in self.Q_TABLE_P2.items():
                writer.writerow([key] + values.tolist())

    def load_q_tables(self, dir: str = '.'):
        script_dir = Path(__file__).resolve().parent
        try:                
            with open(f'{script_dir}/{dir}/q_table_p1.csv') as f:
                reader = csv.reader(f)
                for row in reader:
                    key = row[0]
                    self.Q_TABLE_P1[key] = np.array(row[1:], dtype=np.float32)
            with open(f'{script_dir}/{dir}/q_table_p2.csv') as f:
                reader = csv.reader(f)
                for row in reader:
                    key = row[0]
                    self.Q_TABLE_P2[key] = np.array(row[1:], dtype=np.float32)
        except FileNotFoundError:
            self.save_q_tables()            

    def calculate_reward(self, favorite: int, state: Game, next_state: Game) -> float:
        reward = 0
        if favorite == Game.PLAYER_ONE:
            reward = (len(next_state.max_component_p1) - len(state.max_component_p1)) * 3
        elif favorite == Game.PLAYER_TWO:
            reward = (len(next_state.max_component_p2) - len(state.max_component_p2)) * 3

        state_lines = state.get_lines()
        next_state_lines = next_state.get_lines()        

        for i in range(len(state_lines)):
            score_sl  = state.line_score(favorite, [slot.owner for slot in state_lines[i]])
            score_nsl = next_state.line_score(favorite, [slot.owner for slot in next_state_lines[i]])
            reward += 0.05 * (score_nsl - score_sl)

        if next_state.winner == favorite:
            reward += self.parameters['VICTORY_REWARD']
        elif next_state.winner is None and next_state.end:
            reward += self.parameters['TIE_REWARD']
        elif next_state.end:
            reward += self.parameters['DEFEAT_PENALTY']

        return reward