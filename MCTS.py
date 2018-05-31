import numpy as np
from config import ALPHA, EPSILON
import loggers as lg
import math


class Node:
    def __init__(self, state):
        self.state = state
        self.children = []
        self.stats = {
            'N': 0,  # Number of visits to this node
            'W': 0,  # Accumulated value of this node
        }

    def is_leaf(self):
        return len(self.children) > 0

    def add_child(self, action, node, probability):
        self.children.append({
            'action': action,
            'node': node,
            'P': probability
        })


class MCTS:
    def __init__(self, root, cpuct):
        self.root = root
        self.tree = {}
        self.cpuct = cpuct
        self.add_node(root)

    def __len__(self):
        return len(self.tree)

    def move_to_leaf(self):
        lg.logger_mcts.info('------MOVING TO LEAF------')
        current_node = self.root
        path_to_leaf = [current_node]

        while not current_node.is_leaf():
            lg.logger_mcts.info('PLAYER TURN...%d', current_node.state.player_turn)
            chosen_child = self._choose_child(current_node.children)
            new_state, value, done = current_node.state.take_action(chosen_child['action'])
            current_node = chosen_child['node']
            path_to_leaf.append(chosen_child['node'])

        lg.logger_mcts.info('DONE...%d', done)
        return value, done, path_to_leaf

    def back_fill(self, value, path_to_leaf):
        lg.logger_mcts.info('------DOING BACKFILL------')
        current_player = path_to_leaf[-1].state.player_turn

        for i, (node) in path_to_leaf:
            player_turn = node.state.player_turn
            if player_turn == current_player:
                direction = 1
            else:
                direction = -1

            node.stats['N'] = node.stats['N'] + 1
            node.stats['W'] = node.stats['W'] + value * direction

            lg.logger_mcts.info('updating node with value %f for player %d... N = %d, W = %f, Q = %f'
                                , value * direction
                                , player_turn
                                , node.stats['N']
                                , node.stats['W']
                                , node.stats['W'] / node.stats['N']
                                )
            if i > 0:
                node.state.render(lg.logger_mcts)

    def add_node(self, node):
        self.tree[node.id] = node

    def _choose_child(self, children):
        N_p = sum([child['node'].stats['N'] for child in children])
        max_Q_plus_U = -math.inf
        chosen_child = None

        for i, (child) in enumerate(children):
            action = child['action']
            P_i, N_i, W_i = self._get_child_stats(child, len(children) - 1)
            Q_i = W_i / N_i
            U_i = self.cpuct * P_i * np.sqrt(N_p) / (1 + N_i)  # Using progressive strategy as per http://tiny.cc/gjg6ty

            lg.logger_mcts.info(
                'action: %d ... N = %d, P = %f, nu = %f, W = %f, Q = %f, U = %f, Q+U = %f'
                , action, N_i, np.round(P_i, 6), np.round(nu[i], 6),
                np.round(W_i, 6), np.round(Q_i, 6), np.round(U_i, 6), np.round(Q_i + U_i, 6))

            if Q_i + U_i > max_Q_plus_U:
                max_Q_plus_U = Q_i + U_i
                chosen_child = child
        lg.logger_mcts.info('action with highest Q + U...%d', chosen_child['action'])
        return chosen_child

    def _get_child_stats(self, child, number_of_siblings):
        P = (1 - EPSILON) * child['P'] + EPSILON * np.random.dirichlet([ALPHA] * len(number_of_siblings + 1)) \
            if child['node'] == self.root else child['P']

        return P, \
               child['node'].stats['N'], \
               child['node'].stats['W']
