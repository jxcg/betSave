def submission_check(back_comms, back_odds_decimal, back_stake_input, lay_comms, lay_odds_decimal):
    if not back_comms:
        back_comms = 0
    if not lay_comms:
        lay_comms = 0
    if not back_odds_decimal or not back_stake_input or not lay_odds_decimal:
        return False
    return True

class Bet:
    def __init__(self, back_stake, back_odds, lay_commission, back_commission, lay_odds, bet_type):
        self.back_stake = back_stake
        self.back_odds = back_odds
        self.lay_commission = lay_commission
        self.back_commission = back_commission
        self.lay_odds = lay_odds
        self.bet_type = bet_type

    def get_lay_stake(self):
        if self.bet_type == "Qualifying Bet":
            return round((self.back_stake * self.back_odds) / self.lay_odds, 2)
        return round(self.back_stake * (self.back_odds - 1) / self.lay_odds, 2)

    def get_lay_liability(self):
        return round(self.get_lay_stake() * (self.lay_odds - 1), 2)

    def get_case_back_bet_win(self):
        back_winnings = self.back_stake * (self.back_odds - 1)
        back_winnings -= back_winnings * self.back_commission
        if self.bet_type == "Free Bet":
            return round(back_winnings - self.get_lay_liability(), 2)
        profit = round(back_winnings - self.get_lay_liability(), 2)
        return profit

    def get_case_lay_bet_wins(self):
        lay_winnings = self.get_lay_stake()
        lay_commission_deduction = self.lay_commission * (self.get_lay_stake() * (self.lay_odds - 1))
        if self.bet_type == "Free Bet":
            return round(lay_winnings - lay_commission_deduction, 2)
        profit = round(lay_winnings - lay_commission_deduction - self.back_stake, 2)
        return profit

def calculate(bet_type, back_stake, back_odds, lay_commission, back_commission, lay_odds):
    if submission_check(back_commission, back_odds, back_stake, lay_commission, lay_odds):
        bet = Bet(back_stake, back_odds, lay_commission, back_commission, lay_odds, bet_type)
        results = {
            "Lay Stake": bet.get_lay_stake(),
            "Lay Liability": bet.get_lay_liability(),
            "Profit if Back Wins": bet.get_case_back_bet_win(),
            "Profit if Lay Wins": bet.get_case_lay_bet_wins()
        }
        return results
    else:
        raise ValueError("Invalid input: Please ensure all required inputs are provided.")

