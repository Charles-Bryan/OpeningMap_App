"""
Purpose is to return key statistics of a player's openings to display in the boxes above the opening plot.
Key statistics:
-- Overall stats: Wins, Losses, Draws
-- Most common opening
-- Best opening
-- Worst opening
"""
import pandas as pd
from assets.src.openings import opening_dict

def calculate_results(input_df):
    df = input_df.copy()

    wins = int(df['Wins'].sum())
    losses = int(df['Losses'].sum())
    draws = int(df['Draws'].sum())
    games = int(df.shape[0])
    return wins, losses, draws, games

def get_grouped_games(df, parameters):
    # If an opening is selected, do not include those columns in the calculations
    ply = parameters['Ply']
    opening = opening_dict[parameters['Opening']]

    # Calculate how many ply in we are aggregating based on the ply selected and opening sequence selected
    if parameters["Opening"] == "All Games":
        aggregate_len = ply
    else:
        aggregate_len = ply + len(opening.split(' '))

    # If ply selected plus the opening sequence selected is too long, return  "Ply + Opening Sequence too long"
    if aggregate_len > 20:
        return "Ply + Opening Sequence too long"

    move_cols = [col_name for col_name in df.columns if col_name.startswith("Half")]
    agg_cols = move_cols[:aggregate_len]

    grouped_games = df.groupby(agg_cols).agg(Avg_Result=('Result', 'mean'),
                              Occurrences=('Occurrences', 'sum')).reset_index()

    if grouped_games.shape[0] == 0:
        print("Error Code 1")
        return "No Games Matching this Opening"

    grouped_games = grouped_games[grouped_games['Occurrences']>=parameters["Min_Occur"]]
    if grouped_games.shape[0] == 0:
        return "Insufficient Games. \nTry reducing minimum occurrences or ply."

    return grouped_games

def most_played(input_df, parameters):
    df = input_df.copy()

    grouped_games = get_grouped_games(df, parameters)
    if isinstance(grouped_games, str):
        return "Error", grouped_games

    max_occur = grouped_games["Occurrences"].max()
    selected_row = grouped_games[grouped_games["Occurrences"] == max_occur]
    move_cols = [col_name for col_name in selected_row.columns if col_name.startswith("Half")]
    move_seq = []
    for index, col_name in enumerate(move_cols):
        if index % 2 == 0:
            move_seq.append(str(int(index/2 +1)) + ".")
        move_seq.append(selected_row[col_name].values[0])

    output_seq = (' ').join(move_seq)

    return max_occur, output_seq

def best_opening(input_df, parameters):
    df = input_df.copy()

    grouped_games = get_grouped_games(df, parameters)
    if isinstance(grouped_games, str):
        return "Error", grouped_games

    max_result = grouped_games["Avg_Result"].max()
    selected_row = grouped_games[grouped_games["Avg_Result"] == grouped_games["Avg_Result"].max()]
    move_cols = [col_name for col_name in selected_row.columns if col_name.startswith("Half")]
    move_seq = []
    for index, col_name in enumerate(move_cols):
        if index % 2 == 0:
            move_seq.append(str(int(index/2 +1)) + ".")
        move_seq.append(selected_row[col_name].values[0])

    output_seq = (' ').join(move_seq)
    return max_result, output_seq

def worst_opening(input_df, parameters):
    df = input_df.copy()

    grouped_games = get_grouped_games(df, parameters)
    if isinstance(grouped_games, str):
        return "Error", grouped_games

    min_result = grouped_games["Avg_Result"].min()
    selected_row = grouped_games[grouped_games["Avg_Result"] == grouped_games["Avg_Result"].min()]
    move_cols = [col_name for col_name in selected_row.columns if col_name.startswith("Half")]
    move_seq = []
    for index, col_name in enumerate(move_cols):
        if index % 2 == 0:
            move_seq.append(str(int(index / 2 + 1)) + ".")
        move_seq.append(selected_row[col_name].values[0])

    output_seq = (' ').join(move_seq)
    return min_result, output_seq
