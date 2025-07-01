from game_calculations import GameCalculations
from src.calculations.lines import Lines
from src.events.events import fs_trigger_event


class GameExecutables(GameCalculations):

    def evaluate_lines_board(self):
        """Populate win-data, record wins, transmit events."""
        self.win_data = Lines.get_lines(self.board, self.config, global_multiplier=self.global_multiplier)
        Lines.record_lines_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        Lines.emit_linewin_events(self)

    # Modify these functions to allocate the correct number of spins
    def check_fs_condition(self, scatter_key: str = "scatter") -> bool:
        """Check if there are enough active scatters to trigger fs."""

        if self.count_symbols_on_board("SA") >= min(
            self.config.custom_freespin_triggers[self.gametype]["SA"].keys()
        ) and not (self.repeat):
            return True
        if self.count_symbols_on_board("SB") >= min(
            self.config.custom_freespin_triggers[self.gametype]["SB"].keys()
        ) and not (self.repeat):
            return True
        if self.count_symbols_on_board("SC") >= min(
            self.config.custom_freespin_triggers[self.gametype]["SC"].keys()
        ) and not (self.repeat):
            return True
        return False

    def update_freespin_amount(self, scatter_symbol: str) -> None:
        """
        Set initial number of spins for a freegame and transmit event.
        Alter the counting function to target a specific symbol, as opposed to a symbol type
        """
        self.tot_fs = self.config.custom_freespin_triggers[self.gametype][scatter_symbol][
            self.count_symbols_on_board(scatter_symbol)
        ]
        if self.gametype == self.config.basegame_type:
            basegame_trigger, freegame_trigger = True, False
        else:
            basegame_trigger, freegame_trigger = False, True
        fs_trigger_event(self, basegame_trigger=basegame_trigger, freegame_trigger=freegame_trigger)

    def update_fs_retrigger_amt(self, scatter_key: str = "scatter") -> None:
        """Update total freespin amount on retrigger."""
        self.tot_fs += self.config.custom_freespin_triggers[self.gametype][self.trigger_symbol][
            self.count_symbols_on_board(self.trigger_symbol)
        ]
        fs_trigger_event(self, freegame_trigger=True, basegame_trigger=False)

    # Alter how freespins are recorded
    def run_freespin_from_base(self, scatter_sym: str) -> None:
        """Trigger the freespin function and update total fs amount."""
        assert scatter_sym in self.config.special_symbols["scatter"]
        self.record(
            {
                "kind": self.count_symbols_on_board(scatter_sym),
                "symbol": scatter_sym,
                "gametype": self.gametype,
            }
        )
        self.update_freespin_amount(scatter_sym)

        # Make sure you do not draw a board which can trigger multiple types of freespins
        match self.trigger_symbol:
            case "SA":
                if any(
                    [
                        self.count_symbols_on_board("SB")
                        >= min(self.config.custom_freespin_triggers[self.config.basegame_type]["SB"].keys()),
                        self.count_symbols_on_board("SC")
                        >= min(self.config.custom_freespin_triggers[self.config.basegame_type]["SC"].keys()),
                    ]
                ):
                    self.repeat = True
            case "SB":
                if any(
                    [
                        self.count_symbols_on_board("SA")
                        >= min(self.config.custom_freespin_triggers[self.config.basegame_type]["SA"].keys()),
                        self.count_symbols_on_board("SC")
                        >= min(self.config.custom_freespin_triggers[self.config.basegame_type]["SC"].keys()),
                    ]
                ):
                    self.repeat = True
            case "SC":
                if any(
                    [
                        self.count_symbols_on_board("SA")
                        >= min(self.config.custom_freespin_triggers[self.config.basegame_type]["SA"].keys()),
                        self.count_symbols_on_board("SB")
                        >= min(self.config.custom_freespin_triggers[self.config.basegame_type]["SB"].keys()),
                    ]
                ):
                    self.repeat = True
            case _:
                raise RuntimeError("Scatter-type error")
        self.run_freespin()
