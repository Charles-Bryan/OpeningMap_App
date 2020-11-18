import pandas as pd
import numpy as np
import plotly.express as px
import sqlite3

from Filter_Database import obtain_criteria
from Filter_Database import retrieve_player_db
from Filter_Database import get_half_moves

from openings import opening_dict

path_db = "./databases/"
merged_database_name = path_db + 'Merged_Monthlies.db'

def condition_player_result(row, player_name):
    if (row['BlackName'] == player_name) :
        return abs(row['Result']-1)
    else:
        return row['Result']

def prep_dataframe(input_df, half_moves_list):
    # convert sql object to dataframe ready for the plotly thing
    df = input_df.copy()


    # Two plans, improve path to have a title that could be player name or "Everyone" or whatever"
    # Improve the hover over Data

    return df

if __name__ == "__main__":

    table_name = 'Moves_2013_2015'

    filters = obtain_criteria(list(opening_dict.keys()), force_playerName = True)

    # get path (will also be the half moves needed to be passed into the get sql query function)
    half_moves_list = get_half_moves(table_name)
    # create the query for the SQL database and retrieve the database. Then convert to a pandas dataframe.
    # db = retrieve_db(filters, table_name, half_moves_list)
    # df.columns = ["Avg_Result", "Count"] + half_moves_list
    db = retrieve_player_db(filters, table_name, half_moves_list)
    df = pd.DataFrame(db)
    df.columns = ["WhiteName", "BlackName", "Result"] + half_moves_list
    # Check if anything returned
    if df.shape[0] == 0:
        print("No games returned with the given criteria.")
    else:

        # Modify the player db result to reflect the player's results
        df['Rel_Result'] = df.apply(condition_player_result, args=(filters['input_PlayerName'],), axis=1)

        # Aggregate the player's games
        max_rows = 2000
        grouping_cols = half_moves_list
        df['Count'] = 1

        while True:
            df_agg = df.groupby(grouping_cols).agg(Avg_Result=('Rel_Result', 'mean'), Occurrences=('Count', 'sum')).reset_index()
            num_rows = df_agg.shape[0]
            if num_rows <= max_rows or len(grouping_cols) <= 3:
                break
            else:
                del grouping_cols[-1]

        # Prep the dataframe for the plotly treemap function
        df_agg = prep_dataframe(df_agg, grouping_cols)

        # Prep the path
        Title = filters['input_PlayerName']
        if filters['input_Opening'] != '':
            Title += ": " + filters['input_Opening']
            df_agg["Title"] = Title
            path = ['Title'] + grouping_cols[len(opening_dict[filters['input_Opening']].split()):]
        else:
            df_agg["Title"] = Title
            path = ['Title'] + grouping_cols

        fig = px.treemap(df_agg, path=path, values='Occurrences',
                         color='Avg_Result',
                         # hover_data=['iso_alpha'],
                         color_continuous_scale=["black", "white", "blue"],
                         color_continuous_midpoint=0.5,
                         branchvalues='total')
        fig.show()