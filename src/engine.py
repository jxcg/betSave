class Wager:
    def __init__(self, back_stake, back_odds, back_commission, lay_commission, lay_odds, free):
        self.free               = free # TRUE / FALSE
        self.back_stake         = back_stake # BACK BET is INTERCHANGEABLE to QUALIFYING BET OR FREE BET
        self.back_odds          = back_odds
        self.back_commission    = back_commission
        self.lay_odds           = lay_odds
        self.lay_commission     = lay_commission


    """
    Qualifying bet and welcome bet formulas
    """

    def get_lay_stake(self, free, stake_returned=False):
        if not free:
            return (
                self.back_odds * self.back_stake / (self.lay_odds - self.lay_commission)
                )
        
        if free and not stake_returned:
            ## Free Bet, SNR
            return (
                (self.back_odds - 1) / (self.lay_odds - self.lay_commission) * self.back_stake # free bet in this case
            )

        if free and stake_returned:
            ## Free Bet, SR
            return (
                (self.back_odds * self.back_stake) / (self.lay_odds - self.lay_commission)
            )   




    def profit_if_back_bet_wins(self):
        return (
            self.back_stake * (self.back_odds - 1) - self.get_lay_stake(False) * (self.lay_odds - 1)
            )

    

    def profit_if_lay_bet_wins(self, free):
        if not free:
            return (
                self.get_lay_stake(False) * (1 - self.lay_commission) - self.back_stake
                )

        return (
            self.get_lay_stake(True) * (1 - self.lay_commission)
        )



    def final_profit_for_qualifying_bet(self):
        return self.profit_if_lay_bet_wins(False)


    """
    Free bet - SNR
    """

    def profit_free_bet_wins(self, stake_returned=False):
        if not stake_returned:
            return (
                (self.back_odds - 1) * self.back_stake - (self.lay_odds - 1) * self.get_lay_stake(True)
            )
        
        ## IF STAKE RETURNED
        
        return (
            self.back_stake * self.back_odds - (self.lay_odds - 1) * self.get_lay_stake(True, True) # Free + SR
        )


    
    def final_profit_free_bet(self, stake_returned):
        if not stake_returned:
            return (
                self.get_lay_stake(True) * (1 - self.lay_commission)
            )
        
        # IF FREE + STAKE_RETURNED
        return (
            self.back_stake
        )
