from game_override import GameStateOverride
from src.calculations.lines import Lines
import random


class GameState(GameStateOverride):
    """Handles game logic and events for a single simulation number/game-round."""

    def run_spin(self, sim):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            # Assumes you have specified the frequency of each trigger-type
            if self.get_current_distribution_conditions()["force_freegame"]:
                match self.criteria:
                    case "freegame":
                        self.trigger_symbol = "SA"
                    case "superfreegame":
                        self.trigger_symbol = "SB"
                    case "megafreegame":
                        self.trigger_symbol = "SC"
                    case "wincap":
                        # Any freegame type can potentailly trigger a max-win
                        self.trigger_symbol = random.choice(self.config.special_symbols["scatter"])
                    case _:
                        raise RuntimeError("Invalid criteria")

                self.draw_board(trigger_symbol=self.trigger_symbol)
            else:
                self.draw_board()

            # Evaluate wins, update wallet, transmit events
            self.evaluate_lines_board()

            self.win_manager.update_gametype_wins(self.gametype)
            if self.check_fs_condition():
                self.run_freespin_from_base(scatter_sym=self.trigger_symbol)

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        # NOTE: FR0 reels only contain 'S' symbols. Draw and convert to SA/SB/SC or select special reelset depending on mode
        match self.trigger_symbol:
            case "SA":
                self.run_freespin_one()
            case "SB":
                self.run_freespin_two()
            case "SC":
                self.run_freespin_three()
            case _:
                raise RuntimeError("Trigger-symbol not reconized")

        self.run_old_freespin()  # Just executing this so that the game can complete
        self.end_freespin()

    def run_freespin_one(self):
        "Special logic for SA symbol trigger"

    def run_freespin_two(self):
        "Special logic for SB symbol trigger"

    def run_freespin_three(self):
        "Special logic for SC symbol trigger"

    def run_old_freespin(self):
        """Old function just so that the demo program finishes"""
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board()
            # Swap out the old scatter symbol to SA/SB/SC if it exists
            for idx, _ in enumerate(self.board):
                for idy, _ in enumerate(self.board[idx]):
                    if self.board[idx][idy].name == "S":
                        self.board[idx][idy] = self.create_symbol(self.trigger_symbol)

            self.evaluate_lines_board()

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

            self.win_manager.update_gametype_wins(self.gametype)
