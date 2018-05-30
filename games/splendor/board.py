from noble import Noble
from deck import Deck


class Board:
    player_count = -1
    nobles = []
    decks = []
    chips = -1

    def __init__(self, player_count):
        self.player_count = player_count
        self.reset()

    def reset(self):
        self.nobles = Noble().nobles
        self.decks = [Deck(0), Deck(1), Deck(2)]
        self.chips = self.get_starting_chips

    @property
    def get_starting_chips(self):
        starting_chip_counts = [0, 0, 4, 5, 7]
        starting_chips = (5 << 15)

        for colorIndex in range(0, 5):
            starting_chips += (starting_chip_counts[self.player_count] << (3 * colorIndex))
        return starting_chips

    def get_exposed_cards(self):
        exposed_cards = []
        row = 0

        for deck in self.decks:
            for i in range(0, min(4, len(deck.cards))):
                exposed_cards.append({
                    "row": row,
                    "index": len(deck.cards) - i - 1,
                    "card": deck.cards[len(deck.cards) - i - 1]
                })
            row += 1
        return exposed_cards

    def get_top_cards(self):
        top_cards = []
        row = 0

        for deck in self.decks:
            if len(deck.cards) > 4:
                top_cards.append({
                    "row": row,
                    "index": len(deck.cards) - 5,
                    "card": deck.cards[len(deck.cards) - 5]
                })
            row += 1
        return top_cards

    def remove_card(self, row, index):
        del self.decks[row].cards[index]

    def add_chips(self, chips):
        self.chips += chips

    def remove_chips(self, chips):
        self.chips -= chips

    def get_decks(self):
        return self.decks
