"""
Purpose is to contain functions for modifying an existing dataframe.
Main ideas:
1. Invert Result if Player Choice is Black
2. Reduce number of rows if too great
"""
from assets.src.openings import opening_dict

def correct_results(input_df, params):
    df = input_df
    result_mapping = {
        1.0: 0.0,
        0.0: 1.0,
        0.5: 0.5
    }
    if params["PlayerColor"] == "Black":
        df.loc[:,"Result"] = df["Result"].map(result_mapping)

    return df

def reduce_games(input_df):
    # Skipping for now
    return input_df

def determine_path(input_df, parameters):
    move_cols = [col_name for col_name in input_df.columns if col_name.startswith("Half")]
    if parameters["Opening"] == "All Games":
        return ['Title'] + move_cols

    return ['Title'] + move_cols[len(opening_dict[parameters["Opening"]].split(' ')):]

def correct_dtypes(input_df):
    # Bad hardcoding in here :(
    df = input_df.copy()
    df = df.astype({
        'Result': 'float',
        'Occurrences': 'int32',
        'Wins': 'float',
        'Losses': 'float',
        'Draws': 'float'
    })
    return df

def filter_on_opening(input_df, parameters):

    if parameters["Opening"] == "All Games":
        return input_df

    df = input_df.copy()
    opening = opening_dict[parameters["Opening"]]
    opening_moves = opening.split(' ')
    move_columns = [col_name for col_name in input_df.columns if col_name.startswith("Half")]
    for (move, col) in zip(opening_moves, move_columns[:len(opening_moves)]):
        df = df[df[col] == move]

    return df

