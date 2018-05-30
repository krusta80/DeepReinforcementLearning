from board import Board
from common import *
from moves import Moves
from noble import Noble
from player import Player
from random import shuffle
import functools

class Game:
    board = None
    move = -1
    moves_made = []
    move_options_generator = Moves()
    player_count = -1
    players = []

    def __init__(self, agents):
        self.player_count = 0
        self.players = []
        for agent in agents:
            player = Player(self.player_count, agent.name)
            player.add_agent(agent)
            self.player_count += 1
            self.players.append(player)
        self.board = Board(self.player_count)
        self.reset()

    def reset(self):
        shuffle(self.players)
        for player in self.players:
            player.reset()
        self.board.reset()
        self.move = 0
        self.moves_made = []

    def get_current_player(self):
        return self.players[self.move % self.player_count]

    def log_moves(self):
        print(self.moves_made)

    def play_until_end(self):
        while self.move < 200 and not self.is_over():
            player = self.get_current_player()
            decision = player.agent.make_move(
                self.board, self.players, self.move % self.player_count, self.get_moves(self.board, player))
            self.moves_made.append({
                "turn": self.move,
                "player": self.gather_player_stats(player),
                "move": decision
            })
            self.execute_decision(decision)
            self.move += 1
        if self.move >= 200:
            return {
                "moves": self.move,
                "winner": "TIE!"
            }
        return self.get_outcome()

    def play_until_player_id(self, id):
        game_states = []

        while self.move < 200 and not self.is_over() and self.get_current_player().id != id:
            player = self.get_current_player()
            decision = player.agent.make_move(
                self.board, self.players, self.move % self.player_count, self.get_moves(self.board, player))
            self.moves_made.append({
                "turn": self.move,
                "player": self.gather_player_stats(player),
                "move": decision
            })
            self.execute_decision(decision)
            game_states.append(self.get_game_state(id))
            self.move += 1
        return game_states

    def is_over(self):
        return self.move % self.player_count == 0 and self.get_top_score() >= 15

    def get_top_score(self):
        return functools.reduce(lambda top_score, player: max(top_score, player.points), self.players, -1)

    def execute_decision(self, decision):
        if decision["label"] == "PURCHASE":
            return self.execute_purchase(decision["action"])
        if decision["label"] == "TAKE":
            return self.execute_take(decision["action"])
        if decision["label"] == "RESERVE_EXPOSED":
            return self.execute_reserve(decision["action"], False)
        if decision["label"] == "RESERVE_COVERED":
            return self.execute_reserve(decision["action"], True)

    def execute_purchase(self, action):
        pre_purchase_player_chips = self.get_current_player().chips

        if action["card"].is_reserved:
            self.get_current_player().activate_card(action["card"])
        else:
            self.get_current_player().buy_card(action["card"])
            self.board.remove_card(action["row"], action["index"])
        self.board.add_chips(pre_purchase_player_chips - self.get_current_player().chips)
        self.check_nobles()

    def execute_take(self, action):
        take = int(action.split(',')[0])
        give_back = int(action.split(',')[1])

        self.make_chip_exchange(take, give_back)

    def execute_reserve(self, action, is_covered):
        card = action["card"]["card"]
        take = int(action["chips"].split(',')[0])
        give_back = int(action["chips"].split(',')[1])

        self.board.remove_card(action["card"]["row"], action["card"]["index"])
        self.get_current_player().reserve_card(card, 0)
        self.make_chip_exchange(take, give_back)

    def make_chip_exchange(self, take, give_back):
        self.get_current_player().add_chips(take)
        self.board.remove_chips(take)
        self.get_current_player().remove_chips(give_back)
        self.board.add_chips(give_back)

    def get_outcome(self):
        winner = self.get_winner()

        return {
            "winner": winner,
            "score": self.get_top_score(),
            "moves": self.move
        }

    def get_winner(self):
        self.players.sort(key=lambda player: player.points*100 - len(player.purchased_cards), reverse=True)
        if self.players[0].points == self.players[1].points and \
                len(self.players[0].purchased_cards) == len(self.players[1].purchased_cards):
            return -1
        return self.players[0].id

    def check_nobles(self):
        index = 0
        takeable_nobles = []

        for noble in self.board.nobles:
            takeable_noble = {
                "index": index,
                "noble": noble
            }
            index += 1
            if Noble().can_get_noble(noble, self.get_current_player().card_chip_values):
                takeable_nobles.append(takeable_noble)

        if len(takeable_nobles) > 0:
            taken_noble = self.get_current_player().agent.take_noble(takeable_nobles)
            del self.board.nobles[taken_noble["index"]]
            self.get_current_player().add_noble(taken_noble)

    def gather_player_stats(self, player):
        return {
            "id": player.id,
            "name": player.name,
            "points": player.points,
            "card_summary": player.get_card_and_chip_values(),
            "reserves": player.get_reserved_cards(),
            "chips": translate_chip_count(player.chips),
            "nobles": player.get_nobles()
        }

    def get_game_state(self, player_id):
        return {
            "turn": self.move,
            "board": self.board,
            "players": self.players,
            "moves": self.get_moves(self.board, self.get_current_player()),
            "is_over": self.is_over(),
            "current_player": player_id,
            "winner": self.get_winner(),
            "did_win": self.get_winner() == player_id
        }

    def get_moves(self, board, player):
        return self.move_options_generator.get_moves(board, player)
