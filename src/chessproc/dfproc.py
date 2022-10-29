
import pandas as pd


def add_series(dataframe: pd.DataFrame, func):
    """Adds column to game dataframe by applying the given function to each row, function takes series"""
    dataframe[func.__name__] = dataframe.apply(func, axis=1)


def add_player_specific_series(dataframe: pd.DataFrame, player: str, func):
    """Adds column to game dataframe by applying the given function to each row, function takes series and username"""
    dataframe[f"{func.__name__}"] = dataframe.apply(lambda x: func(x, player), axis=1)


def player_result(series: pd.Series, player: str):
    """Return the score of the player of interest"""
    res = series['Termination'].split()[0]
    if res == player:
        return 1
    elif res == "Game":
        return 0.5
    else:
        return 0


def player_colour(series: pd.Series, player: str) -> str:
    """Return the colour of the player of interest"""
    if player == series["White"]:
        return "White"
    else:
        return "Black"


def elo_difference(series: pd.Series, player: str):
    if player == series['Black']:
        return series['WhiteElo'] - series['BlackElo']
    elif player == series['White']:
        return series['BlackElo'] - series['WhiteElo']
    else:
        return None
    

def game_length(series: pd.Series):
    """Return the length of the game"""
    return len(series['moves'])


def remove_opponent(player_games: pd.DataFrame, *args):
    """Return player dataframe with all games including the listed players removed"""
    return player_games.query(f"White not in {list(args)} & Black not in {list(args)}")
