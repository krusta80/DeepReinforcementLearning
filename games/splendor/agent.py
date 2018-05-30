import functools
import random


class Agent:
    name = ""

    def __init__(self, name):
        self.name = name

    def make_move(self, board, players, player_index, moves):
        #  Random bot (for now)
        if len(moves["purchase"]) > 0:
            return {
                "label": "PURCHASE",
                "action": moves["purchase"][0]
            }

        move_types = [moves["take_chips"], moves["reserve"]["exposed"], moves["reserve"]["covered"]]
        move_labels = ["TAKE", "RESERVE_EXPOSED", "RESERVE_COVERED"]
        total_moves = functools.reduce(lambda subtotal, move_type: subtotal + len(move_type), move_types, 0)
        rand = random.uniform(0, total_moves)
        i = -1

        while rand > 0:
            i += 1
            rand -= len(move_types[i])
        return {
            "label": move_labels[min(i, 2)],
            "action": move_types[min(i, 2)][int(random.uniform(0, len(move_types[min(i, 2)])))]
        }

    def take_noble(self, nobles):
        #  For now, we just take the first available noble.
        return nobles[0]
