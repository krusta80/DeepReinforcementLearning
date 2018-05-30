from chip_moves import ChipMoves


class Moves:
    chip_moves = ChipMoves()

    def get_moves(self, board, player):
        exposed_cards = board.get_exposed_cards()

        return {
            "take_chips": self.chip_moves.get_chip_taking_options(board.chips, player.chips),
            "reserve": self.get_reserve_options(exposed_cards, board.get_top_cards(), board.chips,
                                                player.reserved_cards, player.chips),
            "purchase": self.get_purchase_options(exposed_cards, player.reserved_cards, player.chips_and_cards)
        }

    def get_reserve_options(self, exposed_cards, top_cards, board_chips, reserved_cards, player_chips):
        reserve_chip_options = self.chip_moves.get_reserve_options(board_chips, player_chips)
        options = {
            "exposed": [],
            "covered": []
        }

        if len(reserved_cards) == 3:
            return options

        for card in exposed_cards:
            for option in reserve_chip_options:
                options["exposed"].append({
                    "card": card,
                    "chips": option
                })
        for card in top_cards:
            for option in reserve_chip_options:
                options["covered"].append({
                    "card": card,
                    "chips": option
                })
        return options

    def get_purchase_options(self, exposed_cards, reserved_cards, player_chips_and_cards):
        return [card for card in
                exposed_cards + [{"card": reserved} for reserved in reserved_cards]
                if card["card"].can_be_bought(player_chips_and_cards)]
