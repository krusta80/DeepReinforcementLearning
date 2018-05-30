from moves import *
from deck import *
from board import *
from player import Player

c1 = Card("R", 3, 1, 2)

# for give_back_combo in moves.generate_give_back_combos(9435):  # 2, 2, 3, 3, 3
#     print(translate_chip_count(give_back_combo))

player = Player(0, "Player 1")
board = Board(2)
moves = Moves()

print(moves.get_moves(board, player))
