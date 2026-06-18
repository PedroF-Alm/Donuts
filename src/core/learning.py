import random
import numpy as np
from core.game import Game

class Learning():

    def __init__(self, parameters: dict):
        self.Q_TABLE_P1 = {}
        self.Q_TABLE_P2 = {}  
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
        for p in parameters.keys:
            self.parameters[p] = parameters[p]        

    def train(self, rounds):
        epsilon = self.parameters['INITIAL_EPSILON']
        for r in range(rounds):
            game: Game = Game(seed=self.parameters['SEED'])            
            p1_history = []
            p2_history = []

            while not game.end:
                q_table = get_q_table(game.turn)
                estado_antigo = state(tab, jogador_atual)
                acao = escolher_acao(q_table, tab, jogador_atual, epsilon)
                tab[acao] = jogador_atual
                proximo_jogador = "O" if jogador_atual == "X" else "X"
                proximo_estado = estado(tab, proximo_jogador)

                game.turn = Game.PLAYER_TWO if game.turn == Game.PLAYER_ONE else Game.PLAYER_ONE

                # ==================================
                # SALVA HISTÓRICO
                # ==================================

                if game.turn == Game.PLAYER_ONE:
                    p1_history.append((estado_antigo, acao, proximo_estado))
                else:
                    p2_history.append((estado_antigo, acao, proximo_estado))

                # ==================================
                # VICTORY
                # ==================================
            
                if game.winner == Game.PLAYER_ONE:
                    for (est, ac, prox) in p1_history:
                        self.update_q(self.Q_TABLE_P1, est, ac, self.parameters['VICTORY_REWARD'], prox)
                    for (est, ac, prox) in p2_history:
                        self.update_q(self.Q_TABLE_P2, est, ac, self.parameters['DEFEAT_PENALTY'], prox)
                    break
                elif game.winner == Game.PLAYER_TWO:
                    for (est, ac, prox) in p2_history:
                        self.update_q(self.Q_TABLE_P2, est, ac, self.parameters['VICTORY_REWARD'], prox)
                    for (est, ac, prox) in p1_history:
                        self.update_q(self.Q_TABLE_P1, est, ac, self.parameters['DEFEAT_PENALTY'], prox)
                    break

                # ==================================
                # TIE
                # ==================================

                if game.end and game.winner == None:
                    for (est, ac, prox) in p1_history:
                        self.update_q(self.Q_TABLE_P1, est, ac, self.parameters['TIE_REWARD'], prox)
                    for (est, ac, prox) in p2_history:
                        self.update_q(self.Q_TABLE_P2, est, ac, self.parameters['TIE_REWARD'], prox)
                    break

                game.turn = Game.PLAYER_TWO if game.turn == Game.PLAYER_ONE else Game.PLAYER_ONE

            epsilon = max(self.parameters['EPSILON_MIN'], epsilon * self.parameters['EPSILON_DECAY'])

    def save_q_tables(dir: str):
        pass

    def load_q_tables(dir: str):
        pass
