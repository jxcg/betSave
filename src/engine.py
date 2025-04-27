class Wager:
    def __init__(self, back_stake, back_odds, back_commission, lay_commission, lay_odds, free):
        self.free               = bool(free) # TRUE / FALSE
        self.back_stake         = float(back_stake) # BACK BET is INTERCHANGEABLE to QUALIFYING BET OR FREE BET
        self.back_odds          = float(back_odds)
        self.back_commission    = float(back_commission)
        self.lay_odds           = float(lay_odds)
        self.lay_commission     = float(lay_commission)




    def get_lay_stake(self, free: bool, stake_returned: bool = False) -> float:
        if not free:
            return round(self.back_odds * self.back_stake / (self.lay_odds - self.lay_commission), 2)

        return round(
            ((self.back_odds - 1) if not stake_returned else self.back_odds) * self.back_stake 
            / (self.lay_odds - self.lay_commission),
            2
        )



    def profit_if_back_bet_wins(self) -> float:
        """
        Calculates profit if the back bet wins.
        :return: Profit amount.
        """
        lay_stake = self.get_lay_stake(self.free)
        return round(self.back_stake * (self.back_odds - 1) - lay_stake * (self.lay_odds - 1), 2)




    def profit_if_lay_bet_wins(self) -> float:
        """
        Profit if lay bet wins
        """
        lay_stake = self.get_lay_stake(self.free)

        if not self.free:
            return round(lay_stake * (1 - self.lay_commission) - self.back_stake, 2)

        return round(lay_stake * (1 - self.lay_commission), 2)



    def final_profit_for_qualifying_bet(self) -> float:
        """
        Returns the final profit for a qualifying bet.
        :return: Profit amount.
        """
        return self.profit_if_lay_bet_wins()


    def profit_free_bet_wins(self, stake_returned: bool = False) -> float:
        """
        Calculates profit when a free bet wins.
        :param stake_returned: Whether the free bet stake is returned.
        :return Profit
        """

        lay_stake = self.get_lay_stake(True, stake_returned)
        return round(
            ((self.back_odds - 1) if not stake_returned else self.back_odds) * self.back_stake
            - (self.lay_odds - 1) * lay_stake,
            2
        )

    def final_profit_free_bet(self, stake_returned: bool) -> float:
        """
        Returns the final profit for a free bet.
        :param stake_returned: Whether the free bet stake is returned.
        :return: Profit amount.
        """
        if not stake_returned:
            return round(self.get_lay_stake(True) * (1 - self.lay_commission), 2)
        return round(self.back_stake, 2)