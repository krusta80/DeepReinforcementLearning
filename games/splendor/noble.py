from random import shuffle


class Noble:
    nobles = [
        [4, 0, 0, 4, 0],
        [0, 0, 4, 0, 4],
        [4, 4, 0, 0, 0],
        [0, 4, 4, 0, 0],
        [0, 0, 0, 4, 4],
        [0, 0, 3, 3, 3],
        [3, 3, 3, 0, 0],
        [3, 3, 0, 3, 0],
        [3, 0, 0, 3, 3],
        [0, 3, 3, 0, 3],
    ]

    def __init__(self):
        shuffle(self.nobles)

    def can_get_noble(self, noble_costs, player_card_counts):
        for i in range(0, 5):
            if noble_costs[i] > player_card_counts[i]:
                return False
        return True
