import dash_core_components as dcc
import dash_html_components as html

from assets.src import css_styles as cs
from assets.src.openings import opening_options

import chess
import chess.svg


def setup_layout(app, default_parameters):
    # App layout

    # ------------------------------------------------------------------------------------------------------------------
    # Left SideBar
    sidebar = html.Div(
        [
            html.P("OpeningMap", style=cs.LOGO),
            html.H2("Search Settings", style=cs.HEADING_2),
            html.Hr(),
            # ----------------------------------------------------------------------------
            html.P("Enter a Lichess username", style=cs.SIDEBAR_TEXT),
            dcc.Input(id="input_PlayerName",
                      type="text",
                      value=default_parameters["PlayerName"],
                      style={'margin-right': '1rem',}
                      ),
            html.Button('Submit',
                        id='submit-val',
                        n_clicks=0,
                        style={"background-color": "darkgray"}
                        ),
            html.Hr(),
            # ----------------------------------------------------------------------------
            html.P("Which color pieces?", style=cs.SIDEBAR_TEXT),
            dcc.RadioItems(
                id="select_PlayerColor",
                options=[
                    {'label': 'White', 'value': 'White'},
                    {'label': 'Black', 'value': 'Black'}
                ],
                value=default_parameters["PlayerColor"],
                labelStyle={'display': 'inline-block'}),
            html.Hr(),
            # ----------------------------------------------------------------------------
            html.P("Which time controls?", style=cs.SIDEBAR_TEXT),
            dcc.Checklist(
                id="select_GameTypes",
                options=[
                    {'label': 'Rapid', 'value': 'rapid_True'},
                    {'label': 'Classical', 'value': 'classical_True'}
                ],
                value=['rapid_True' if default_parameters["Rapid_Games"] else '',
                       'classical_True' if default_parameters["Classical_Games"] else '']
            ),
            html.Hr(),
            # ----------------------------------------------------------------------------
            html.P("Choose an Opening (optional)", style=cs.SIDEBAR_TEXT),
            dcc.Dropdown(id="select_opening",
                         options=opening_options,
                         multi=False,
                         value=default_parameters["Opening"],
                         ),
            html.Hr(),
            # ----------------------------------------------------------------------------
            html.H3("Summary Statistics Settings", style=cs.HEADING_3),
            html.Hr(),
            # ----------------------------------------------------------------------------
            html.Div([
                html.P("Set the number of ply",
                   style={'display': 'inline-block', 'margin-top': '0px', "margin-bottom": "0px"}),
                html.P("Ex. 1.e4 e5 would be 2 ply",
                       style={"font-weight": "bolder", "font-size": "small", "margin": "0px"}),
                ], style={"width": '78%', 'display': 'inline-block',}),
            dcc.Input(
                id="select_ply",
                type="number",
                debounce=True,
                min=1, max=16, step=1,
                value=default_parameters["Ply"],
                style={"width": '15%', 'display': 'inline-block', 'margin-top': '0.45rem', 'vertical-align': 'top'},
            ),
            html.Hr(),
            # ----------------------------------------------------------------------------
            html.P("Set the minimum occurrences",
                   style={"width": '78%', 'display': 'inline-block', 'vertical-align': 'center',
                          'margin-top': '0rem', 'margin-bottom': '0rem'}),
            dcc.Input(
                id="select_min_occur",
                type="number",
                debounce=True,
                min=1, max=100, step=1,
                value=default_parameters["Min_Occur"],
                style={"width": '15%', 'display': 'inline-block', 'vertical-align': 'center'},
            ),
            html.Hr(),
            # ----------------------------------------------------------------------------
            html.H3("Contact Info", style=cs.HEADING_3),
            html.Hr(),
            # ----------------------------------------------------------------------------
            html.P("Email:       OpeningMap@gmail.com"),
        ],
        style=cs.SIDEBAR_STYLE,
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Main Body Sections
    Top_Row = html.Div([
            html.Div([
                html.Img(
                    src=app.get_asset_url("/images/E4_is_Best_image.png"),
                    alt="Super Awesome Image did not load. Hopefully your fault.",
                    id="img-top-left",
                    style=cs.TOP_LEFT_IMAGE,
                )
            ], style=cs.TOP_LEFT_BOX),
            html.Div([
                html.Div([
                    html.H1("OpeningMap", style=cs.HEADING_1),
                    html.H3("Exploring Chess Openings with Pretty Plots", style={'text-align': 'center'}),
                    ]),
            ], style=cs.TOP_CENTER_BOX),
            html.Div([
                html.Img(
                    src=app.get_asset_url("/images/resign.png"),
                    alt="Super Awesome Image did not load. Hopefully your fault.",
                    id="img-top-right",
                    style=cs.TOP_RIGHT_IMAGE,
                ),
            ], style=cs.TOP_RIGHT_BOX),
        ], style=cs.TOP_BOX)

    Stat_Box_Row = html.Div([
            html.Div([
                html.P("OVERALL STATS", id="BOX1_HEADER", style=cs.BOX_HEADER),
                html.Div([html.P(id="BOX1_GAMES", children=[],
                                 style=cs.BOX1_TEXT_LEFT
                                 ),
                          html.P(id="BOX1_WINS", children=[],
                                 style=cs.BOX1_TEXT_RIGHT
                                 ),
                          html.P(id="BOX1_LOSSES", children=[],
                                 style=cs.BOX1_TEXT_LEFT
                                 ),
                          html.P(id="BOX1_DRAWS", children=[],
                                 style=cs.BOX1_TEXT_RIGHT
                                 ),
                          ], style=cs.MID_INNER_BOXES)
                     ], style=cs.MID_OUTER_BOXES),
            html.Div([
                html.P("MOST FREQUENT OPENING", id="BOX2_HEADER", style=cs.BOX_HEADER),
                html.Div([
                    html.P(id="BOX2_STMT", children=[], style=cs.BOX_STMT),
                    html.P(id="BOX2", children=[], style=cs.BOX_STMT)],
                    style=cs.MID_INNER_BOXES)
                     ], style=cs.MID_OUTER_BOXES),
            html.Div([
                html.P("BEST OPENING", id="BOX3_HEADER", style=cs.BOX_HEADER),
                html.Div([
                    html.P(id="BOX3_STMT", children=[], style=cs.BOX_STMT),
                    html.P(id="BOX3", children=[], style=cs.BOX_STMT)],
                    style=cs.MID_INNER_BOXES)
                     ], style=cs.MID_OUTER_BOXES),
            html.Div([
                html.P("WORST OPENING", id="BOX4_HEADER", style=cs.BOX_HEADER),
                html.Div([
                    html.P(id="BOX4_STMT", children=[], style=cs.BOX_STMT),
                    html.P(id="BOX4", children=[], style=cs.BOX_STMT)],
                    style=cs.MID_INNER_BOXES)
                     ], style=cs.MID_OUTER_BOXES),
        ], style=cs.MIDDLE_BOX)

    Main_Plot_Section = html.Div([
            html.Div(id='player_name_txt', children=[],
                     style={'font-size': 'xx-large',
                            'margin-top': '1rem',
                            'margin-bottom': '0.25rem'}),
            dcc.Graph(id='Opening_Map', figure={},
                      ),
            html.P("Data Last Updated on 8/31/2020", id="Last_Update", style=cs.LAST_UPDATE),
        ])

    Chess_Board_Row = html.Div([
            html.Div([
                html.Div([
                    html.Div(id='Chess_SVG', children=[], style={'width': '18rem', 'margin-top': '1rem'}),
                    html.A(
                        html.Button('Open in Lichess Analysis', style={'margin-left': '4rem', 'background-color': 'darkgray'}),
                        id='Lichess_Link', href='https://lichess.org/analysis')
                ], style=cs.CHESS_SVG),
            ], style=cs.BOARD_ROW)
        ])

    # Vertically Stack the sections
    main = html.Div([Top_Row, Stat_Box_Row, Main_Plot_Section, Chess_Board_Row], style=cs.CONTENT_STYLE)

    return html.Div([sidebar, main])