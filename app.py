import sys

import pandas as pd
import plotly.express as px

import dash
from dash.dependencies import Input, Output, State

from assets.src.AWS_connection import retrieve_player_db
import assets.src.dataframe_adjustments as da
from assets.src.secure import *
from assets.src.html_layout import setup_layout


app = dash.Dash(__name__)

# ------------------------------------------------------------------------------
# Set up One time data events

# populate db credentials. Credentials masked by gitignore
db_config = {
    'user': user,
    'password': pwd,
    'host': host,
    'raise_on_warnings': True
}

default_parameters = {
    "PlayerName": 'E4_is_Better',
    "PlayerColor": 'White',
    "Rapid_Games": True,
    "Classical_Games": True,
    "Opening": 'All Games'
    # "Start_Date": pass
    # "End_Date": pass
}
parameters = default_parameters
# ------------------------------------------------------------------------------
# app layout (separated into html_layout.py & css_layout.py)
app.layout = setup_layout(app)
# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    Output(component_id='Opening_Map', component_property='figure'),  # 2nd output of return statement
    [Input(component_id='submit-val', component_property='n_clicks'),
     Input(component_id='select_PlayerColor', component_property='value'),
     Input(component_id='select_GameTypes', component_property='value'),
     Input(component_id='select_opening', component_property='value'),
     State(component_id='input_PlayerName', component_property='value')]
)
def update_my_graph(_, Color, GameTypes, Opening, Name):
    print(f"Name: {Name}")
    print(f"Color: {Color}")
    print(f"GameTypes: {GameTypes}")
    print(f"Opening: {Opening}")

    # Name Related actions------------------------------------------------------------
    # output_text = f"The name chosen by user was: {Name}"
    parameters["PlayerName"] = Name

    # Color related actions-----------------------------------------------------------
    parameters["PlayerColor"] = Color
    # GameType related actions--------------------------------------------------------
    if 'rapid_True' in GameTypes:
        parameters["Rapid_Games"] = True
    else:
        parameters["Rapid_Games"] = False
    if 'classical_True' in GameTypes:
        parameters["Classical_Games"] = True
    else:
        parameters["Classical_Games"] = False
    if len(GameTypes) == 0:
        parameters["Rapid_Games"] = True
        parameters["Classical_Games"] = True
    # GameType related actions--------------------------------------------------------
    parameters["Opening"] = Opening

    # --------------------------------------------------------------------------------------
    # Data Retrieval and modifications

    # Get all player's games for the appropriate color
    data = retrieve_player_db(parameters, db_config)

    # Column names. Can be retrieved from the database.table but can hardcode since it will be consistent
    col_names = ['WhiteName', 'BlackName', 'Result', 'Half_Move_1', 'Half_Move_2', 'Half_Move_3', 'Half_Move_4',
                 'Half_Move_5', 'Half_Move_6', 'Half_Move_7', 'Half_Move_8', 'Half_Move_9', 'Half_Move_10',
                 'Half_Move_11', 'Half_Move_12', 'Half_Move_13', 'Half_Move_14', 'Half_Move_15', 'Half_Move_16',
                 'Half_Move_17', 'Half_Move_18', 'Half_Move_19', 'Half_Move_20']
    # Convert data to a df
    df = pd.DataFrame(data, columns=col_names)
    # Filter games on the opening (if one is selected)
    df = da.filter_on_opening(df, parameters)
    # IF PlayerColor IS BLACK, remap the results using a dict. 1->0, 0->1 .5 -> 0.5
    df = da.correct_results(df, parameters)
    # add Occurrences column for grouping operations
    df["Occurrences"] = 1
    # add columns for # of wins, # of losses, # of draws.
    # Couldn't get the hover data to work, but leaving this optimistically
    df["Wins"] = 0
    df.loc[df["Result"] == 1.0, 'Wins'] = 1
    df["Losses"] = 0
    df.loc[df["Result"] == 0.0, 'Losses'] = 1
    df["Draws"] = 0
    df.loc[df["Result"] == 0.5, 'Draws'] = 1

    # If someone, somehow, has over 3000(?) games, then plotly gets slow. Function to reduce that.
    # A placeholder for now.
    df = da.reduce_games(df)

    # path steps -----------------
    df["Title"] = f"{parameters['Opening']}"
    plot_path = da.determine_path(df, parameters)
    # ----------------------------

    # Correct the datatypes for aggregation and plotting
    df = da.correct_dtypes(df)
    df_agg = df.groupby(plot_path).agg(Avg_Result=('Result', 'mean'),
                                       Occurrences=('Occurrences', 'sum'),
                                       Wins=('Wins', 'sum'),
                                       Losses=('Losses', 'sum'),
                                       Draws=('Draws', 'sum')).reset_index()
    # ------------------------------------------------------------------------------------------------------------------

    # Plotly Express
    fig = px.treemap(df_agg, path=plot_path, values='Occurrences',
                     color='Avg_Result',
                     # hover_data=['iso_alpha'],
                     color_continuous_scale=["black", "white", "blue"],
                     color_continuous_midpoint=0.5,
                     branchvalues='total',
                     height=300)
    fig.update_traces(hovertemplate=(
                      'Move:   %{label}<br>'
                      'Occurrences:   %{value}<br>'
                      'Average Result:   %{color:.2f}<br><br>'
                      # 'Wins:   %{customdata[0]:.2f}<br>'
                      # 'Losses:   %{customdata[1]:.2f}<br>'
                      # 'Draws:   %{customdata[2]:.2f}'
                      '<extra></extra>'))
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor="white",
    )

    return fig

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)