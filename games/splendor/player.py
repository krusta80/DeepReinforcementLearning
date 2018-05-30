from common import *


class Player:
    agent = None
    card_chip_values = []
    chips = -1
    chips_and_cards = -1
    id = -1
    name = ""
    nobles = []
    points = -1
    purchased_cards = []
    reserved_cards = []

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.reset()

    def __str__(self):
        return """  
            ========PLAYER=========
            id: {0}
            name: {1}
            points: {2}
            chips: {3}
            chips_and_cards: {4}
            nobles: {5}
            =======================
        """\
            .format(self.id, self.name, self.points, self.chips, self.chips_and_cards, self.nobles)

    def reset(self):
        self.purchased_cards = []
        self.card_chip_values = [0, 0, 0, 0, 0]
        self.reserved_cards = []
        self.nobles = []
        self.points = 0
        self.chips = 0
        self.chips_and_cards = 0

    def buy_card(self, card):
        if card.buy(self.id, self.chips_and_cards):
            self.pay_for_card(card)
            self.purchased_cards.append(card)
            self.points += card.points
            self.card_chip_values[get_color_index(card.color)] += 1
            self.update_chips_and_cards(self.chips)
        else:
            print("ERROR: Cannot buy card (", str(card), ")")

    def reserve_card(self, card, gold):
        if len(self.reserved_cards) >= 3:
            print("ERROR:  Player's reserves are maxed out!")
            return False
        if card.reserve(self.id):
            self.chips += ((gold & 1) << 15)
            self.chips_and_cards += ((gold & 1) << 15)
            self.reserved_cards.append(card)
            if card.owner != self.id:
                print("ERROR:  Owner mismatch!")
            return True
        return False

    def activate_card(self, card):
        reserved_count = len(self.reserved_cards)

        self.reserved_cards = [reserved for reserved in self.reserved_cards if reserved.cost != card.cost]
        if reserved_count == len(self.reserved_cards):
            print("ERROR:  Card not found in player's reserved pile!")
            print(str(card))
            print(self.reserved_cards)
            return False
        self.buy_card(card)

    def pay_for_card(self, card):
        chip_total = self.chips
        gold_chips_needed = 0

        for color_index in range(0, 5):
            color_balance_after_cards = max(0,
                                            ((card.cost >> (3 * color_index)) & 3) - self.card_chip_values[color_index])

            self.chips = (self.chips & (((1 << 18) - 1) - (7 << (3 * color_index)))) + \
                         (max(0, (chip_total & 7) - color_balance_after_cards) << (3 * color_index))
            gold_chips_needed += max(0, color_balance_after_cards - (chip_total & 7))
            chip_total = chip_total >> 3
        self.chips -= (gold_chips_needed << 15)

    def add_chips(self, chips):
        self.chips += chips
        self.update_chips_and_cards(self.chips)

    def remove_chips(self, chips):
        self.add_chips(-1 * chips)

    def update_chips_and_cards(self, chips):
        self.chips_and_cards = 0
        for color_index in range(0, 5):
            self.chips_and_cards += min(7, self.card_chip_values[color_index] + (chips & 7)) << (3 * color_index)
            chips = chips >> 3
        self.chips_and_cards += (chips << 15)

    def add_noble(self, noble):
        self.nobles.append(noble)
        self.points += 3

    def get_card_and_chip_values(self):
        return self.card_chip_values[:]

    def get_reserved_cards(self):
        return self.reserved_cards[:]

    def get_nobles(self):
        return self.nobles[:]

    def add_agent(self, agent):
        self.agent = agent
