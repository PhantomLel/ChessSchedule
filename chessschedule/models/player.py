class Player:
    def __init__(self, name, uid):
        self.name = name
        self.uid = uid
        self.rating = 1000
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.elo_coefficient = 400 # a player with a 400 point advantage over their opponent is ten times more likely to win than to lose; larger value = wider range of rankings
        self.k_factor = 40 # larger number creates a larger change in elo

    def change_rating(self, opp_rating, game_result):
        """
        change_rating updates the player's rating
        :param opp_rating: the rating of the opponent player pre-match
        :param game_result: game result represented as 1 for win, 0.5 for draw, and 0 for loss
        
        Reference: https://www.omnicalculator.com/sports/elo#elo-calculator-in-practice-elo-rating-in-a-chess-tournament
        """
        # Update player stats
        if game_result == 1:
            self.wins += 1
        elif game_result == .5:
            self.draws += 1
        else:
            self.losses += 1

        # Calculate new rating
        expected_score = 1/(1+10**((opp_rating-self.rating)/self.elo_coefficient))
        self.rating = round(self.rating + self.k_factor*(game_result-expected_score), 1)