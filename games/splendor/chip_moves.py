from array import array


class ChipMoves:
    # Code responsible for enumerating all valid chip-taking (and returning)
    # moves for a player, indexed by middle chip counts (and player counts)

    single_chip_array = array('l')
    double_chip_array = array('l')
    give_back_array = {}

    def __init__(self):
        self.single_chip_array = self.generate_single_chip_pile_array()
        self.double_chip_array = self.generate_double_chip_pile_array()
        self.give_back_array = self.generate_give_backs()

    def get_chip_taking_options(self, middle_chips_count, player_chips_count):
        combined_take_and_give_back = []
        combined_take_array = self.single_chip_array[self.get_singles(middle_chips_count)] + self.double_chip_array[
            self.get_doubles(middle_chips_count)]

        for take_option in combined_take_array:
            key = str(player_chips_count + take_option)
            give_back_options = self.give_back_array[key] if key in self.give_back_array else []
            
            if len(give_back_options) == 0:
                combined_take_and_give_back.append(str(take_option) + ',0')
            else:
                for give_back_option in give_back_options:
                    if take_option & give_back_option == 0:
                        combined_take_and_give_back.append(str(take_option) + ',' + str(give_back_option))

        return combined_take_and_give_back

    def get_reserve_options(self, middle_chips_count, player_chips_count):
        take = (middle_chips_count >> 15) & 1
        options = []

        if take == 0:
            return ['0,0']
        elif self.count_chips(player_chips_count) < 10:
            return [str(1 << 15) + ',0']

        for color_index in range(0, 5):
            if player_chips_count & (7 << (3 * color_index)) > 0:
                options.append(str(1 << 15) + ',' + str(1 << (3 * color_index)))
        return options

    def get_singles(self, x):
        singles = 0

        for color_index in range(0, 5):
            singles = singles << 1
            if (x & 7) > 0:
                singles += 1
            x = x >> 3
        return singles

    def get_doubles(self, x):
        doubles = 0

        for color_index in range(0, 5):
            doubles = doubles << 1
            if (x & 7) > 3:
                doubles += 1
            x = x >> 3
        return doubles

    def generate_single_chip_pile_array(self):
        single_chip_pile_combos = []

        for x in range(0, 32):
            single_chip_pile_combos.append(self.generate_single_chip_combos(x))
        return single_chip_pile_combos

    def generate_double_chip_pile_array(self):
        double_chip_pile_combos = []

        for x in range(0, 32):
            double_chip_pile_combos.append(self.generate_double_chip_combos(x))
        return double_chip_pile_combos

    def generate_single_chip_combos(self, x):
        single_chip_combos = array('l')

        for i in range(0, x + 1):
            if self.has_three_or_fewer_bits(i):
                single_chip_combos.append(self.interweave_zeroes(i))
        return single_chip_combos

    def generate_double_chip_combos(self, x):
        double_chip_combos = array('l')

        for i in range(0, 5):
            if x & (1 << i) > 0:
                double_chip_combos.append(1 << (3 * i + 1))
        return double_chip_combos

    def has_three_or_fewer_bits(self, i):
        bit_count = 0

        while i > 0:
            bit_count += i & 1
            i = i >> 1
        return bit_count <= 3

    def interweave_zeroes(self, i):
        interwoven = 0
        mask_bit = 0

        while i > 0:
            interwoven = interwoven | ((i & 1) << (3 * mask_bit))
            mask_bit += 1
            i = i >> 1
        return interwoven

    def generate_give_backs(self):
        give_backs = {}

        for x in range(0, (1 << 18) - 2):
            chip_count = self.count_chips(x)
            if 11 <= chip_count <= 13:
                #print('x is ', x)
                give_backs[x] = self.generate_give_back_combos(x)
        return give_backs

    def count_chips(self, x):
        total_chips = 0

        for i in range(0, 6):
            total_chips += (x & 7)
            x = x >> 3
        return total_chips

    def generate_give_back_combos(self, x):
        give_back_combos = {}

        self.find_give_back_combos(self.extract_chips(x), 0, 0, self.count_chips(x) - 10, give_back_combos)
        return list(give_back_combos.keys())

    def extract_chips(self, x):
        chips = array('l')

        for i in range(0, 6):
            for j in range(0, x & 7):
                chips.append(1 << (3 * i))
            x = x >> 3
        return chips

    def find_give_back_combos(self, chips, next_chip_index, combo, overflow, give_back_combos):
        if overflow <= 0:
            return
        for i in range(next_chip_index, len(chips) - overflow + 1):
            self.find_give_back_combos(chips, i + 1, combo + chips[i], overflow - 1, give_back_combos)
