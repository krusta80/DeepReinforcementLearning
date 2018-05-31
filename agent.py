# %matplotlib inline

import numpy as np
import random

import MCTS as mc
import config
import loggers as lg
import time

import matplotlib.pyplot as plt
from IPython import display
import pylab as pl


class User:
    def __init__(self, name, state_size, action_size):
        self.name = name
        self.state_size = state_size
        self.action_size = action_size

    def act(self, state, tau):
        action = int(input('Enter your chosen action: '))
        pi = np.zeros(self.action_size)
        pi[action] = 1
        value = None
        NN_value = None
        return (action, pi, value, NN_value)


class Agent:
    def __init__(self, name, state_size, action_size, mcts_simulations, cpuct, model):
        self.name = name

        self.state_size = state_size
        self.action_size = action_size

        self.cpuct = cpuct

        self.MCTS_simulations = mcts_simulations
        self.model = model

        self.mcts = None

        self.train_overall_loss = []
        self.train_value_loss = []
        self.train_policy_loss = []
        self.val_overall_loss = []
        self.val_value_loss = []
        self.val_policy_loss = []

    def simulate(self):
        lg.logger_mcts.info('ROOT NODE...%s', self.mcts.root.state.id)
        self.mcts.root.state.render(lg.logger_mcts)
        lg.logger_mcts.info('CURRENT PLAYER...%d', self.mcts.root.state.player_turn)

        ##### MOVE THE LEAF NODE
        value, done, path_to_leaf = self.mcts.move_to_leaf()
        path_to_leaf[-1].state.render(lg.logger_mcts)

        ##### EVALUATE THE LEAF NODE
        value, path_to_leaf = self.evaluate_leaf(value, done, path_to_leaf)

        ##### BACKFILL THE VALUE THROUGH THE TREE
        self.mcts.back_fill(value, path_to_leaf)

    def act(self, state, tau):
        if self.mcts is None or state.id not in self.mcts.tree:
            self.build_MCTS(state)
        else:
            self.change_root_MCTS(state)

        #### run the simulation
        for sim in range(self.MCTS_simulations):
            lg.logger_mcts.info('***************************')
            lg.logger_mcts.info('****** SIMULATION %d ******', sim + 1)
            lg.logger_mcts.info('***************************')
            self.simulate()

        #### get action values
        pi, values = self.get_AV(1)

        ####pick the action
        action, value = self.choose_action(pi, values, tau)

        next_state, _, _ = state.take_action(action)

        NN_value = -self.get_preds(next_state)[0]

        lg.logger_mcts.info('ACTION VALUES...%s', pi)
        lg.logger_mcts.info('CHOSEN ACTION...%d', action)
        lg.logger_mcts.info('MCTS PERCEIVED VALUE...%f', value)
        lg.logger_mcts.info('NN PERCEIVED VALUE...%f', NN_value)
        return action, pi, value, NN_value

    def get_preds(self, state):
        # predict the leaf
        input_to_model = np.array([self.model.convert_to_model_input(state)])

        values, logits = self.model.predict(input_to_model)
        mask = np.ones(logits[0].shape, dtype=bool)
        mask[state.allowed_actions] = False
        logits[0][mask] = -100

        # SOFTMAX
        odds = np.exp(logits[0])
        return values[0], odds / np.sum(odds), state.allowed_actions

    def evaluate_leaf(self, value, done, path_to_leaf):
        leaf = path_to_leaf[-1]
        lg.logger_mcts.info('------EVALUATING LEAF------')

        if done == 0:
            value, probs, allowed_actions = self.get_preds(leaf.state)
            lg.logger_mcts.info('PREDICTED VALUE FOR %d: %f', leaf.state.player_turn, value)

            probs = probs[allowed_actions]      # Implement filter? (JAG)

            for i, action in enumerate(allowed_actions):
                new_state, _, _ = leaf.state.take_action(action)
                if new_state.id not in self.mcts.tree:
                    node = mc.Node(new_state)
                    self.mcts.add_node(node)
                    lg.logger_mcts.info('added node...%s...p = %f', node.id, probs[i])
                else:
                    node = self.mcts.tree[new_state.id]
                    lg.logger_mcts.info('existing node...%s...', node.id)
                leaf.add_child(action, node, probs[i])
        else:
            lg.logger_mcts.info('GAME VALUE FOR %d: %f', leaf.player_turn, value)
        return value, path_to_leaf

    def get_AV(self, tau):
        children = self.mcts.root.children
        pi = np.zeros(self.action_size, dtype=np.integer)
        values = np.zeros(self.action_size, dtype=np.float32)

        for child in children:
            pi[child['action']] = pow(child.stats['N'], 1/tau)
            values[child['action']] = child.stats['W'] / child.stats['N']
        pi = pi / (np.sum(pi) * 1.0)
        return pi, values

    def choose_action(self, pi, values, tau):
        if tau == 0:
            actions = np.argwhere(pi == max(pi))
            action = random.choice(actions)[0]
        else:
            action_idx = np.random.multinomial(1, pi)
            action = np.where(action_idx == 1)[0][0]
        value = values[action]
        return action, value

    def replay(self, ltmemory):
        lg.logger_mcts.info('******RETRAINING MODEL******')
        
        for i in range(config.TRAINING_LOOPS):
            minibatch = random.sample(ltmemory, min(config.BATCH_SIZE, len(ltmemory)))

            training_states = np.array([self.model.convertToModelInput(row['state']) for row in minibatch])
            training_targets = {'value_head': np.array([row['value'] for row in minibatch])
                                , 'policy_head': np.array([row['AV'] for row in minibatch])}

            fit = self.model.fit(training_states, training_targets, epochs=config.EPOCHS, verbose=1, validation_split=0, batch_size = 32)
            lg.logger_mcts.info('NEW LOSS %s', fit.history)

            self.train_overall_loss.append(round(fit.history['loss'][config.EPOCHS - 1],4))
            self.train_value_loss.append(round(fit.history['value_head_loss'][config.EPOCHS - 1],4))
            self.train_policy_loss.append(round(fit.history['policy_head_loss'][config.EPOCHS - 1],4))

        plt.plot(self.train_overall_loss, 'k')
        plt.plot(self.train_value_loss, 'k:')
        plt.plot(self.train_policy_loss, 'k--')

        plt.legend(['train_overall_loss', 'train_value_loss', 'train_policy_loss'], loc='lower left')

        display.clear_output(wait=True)
        display.display(pl.gcf())
        pl.gcf().clear()
        time.sleep(1.0)

        print('\n')
        self.model.printWeightAverages()

    def predict(self, inputToModel):
        preds = self.model.predict(inputToModel)
        return preds

    def buildMCTS(self, state):
        lg.logger_mcts.info('****** BUILDING NEW MCTS TREE FOR AGENT %s ******', self.name)
        self.root = mc.Node(state)
        self.mcts = mc.MCTS(self.root, self.cpuct)

    def changeRootMCTS(self, state):
        lg.logger_mcts.info('****** CHANGING ROOT OF MCTS TREE TO %s FOR AGENT %s ******', state.id, self.name)
        self.mcts.root = self.mcts.tree[state.id]