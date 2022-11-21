from typing import Tuple

ELO_COEFFICIENT = 400  # a player with a 400 point advantage over their opponent is ten times more likely to win than to lose; larger value = wider range of rankings
K_FACTOR = 40  # larger number creates a larger change in elo


def change_rating(player1_rating, player2_rating, game_result) -> Tuple[int, int]:
    """
    change_rating updates the player's rating
    :param player1_rating: the rating of the first player pre-match
    :param player2_rating: the rating of the opponent player pre-match
    :param game_result: tuple of game result represented as 1 for win, 0.5 for draw, and 0 for loss
    :return: tuple of new ratings

    Reference: https://www.omnicalculator.com/sports/elo#elo-calculator-in-practice-elo-rating-in-a-chess-tournament
    """

    # Calculate new rating
    # Player 1
    expected_score = 1 / (
        1 + 10 ** ((player2_rating - player1_rating) / ELO_COEFFICIENT)
    )
    new_rating1 = round(player1_rating + K_FACTOR * (game_result[0] - expected_score))
    # Player 2
    expected_score = 1 / (
        1 + 10 ** ((player1_rating - player2_rating) / ELO_COEFFICIENT)
    )
    new_rating2 = round(player2_rating + K_FACTOR * (game_result[1] - expected_score))

    return (new_rating1, new_rating2)
