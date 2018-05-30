from common import translate_chip_count


class Card:
    color = ''
    points = 0
    cost = 0
    tier = 0
    owner = -1
    is_reserved = False

    def __init__(self, color, points, cost, tier):
        self.color = color
        self.points = points
        self.cost = cost
        self.tier = tier
        self.owner = -1
        self.is_reserved = False

    def __str__(self):
        return 'color: ' + self.color + ' points: ' + str(self.points) \
               + ' cost: ' + translate_chip_count(self.cost)

    def buy(self, player, chips):
        return self.can_be_bought(chips) and self.possess(player)

    def reserve(self, player):
        if self.possess(player):
            self.is_reserved = True
            return True

    def activate(self):
        if not self.is_reserved:
            print("Error:  This card is not currently reserved. %d" % self.owner)
            return False
        self.is_reserved = False
        return True

    def possess(self, player):
        if self.owner != -1 and (self.owner != player or not self.is_reserved):
            print("Error:  This card cannot be transferred. %d" % self.owner)
            return False
        self.owner = player
        return True

    def can_be_bought(self, chips):
        number_of_chips_short_by = 0

        for color_index in range(0, 5):
            number_of_chips_short_by += max(0, ((self.cost >> (3 * color_index)) & 7) - (chips & 7))
            chips = chips >> 3
        return (chips & 7) >= number_of_chips_short_by
