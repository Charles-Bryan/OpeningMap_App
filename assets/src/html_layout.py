import dash_core_components as dcc
import dash_html_components as html

from assets.src import css_styles as cs
from assets.src.openings import opening_options


def setup_layout(app, default_parameters):
    # App layout

    # SideBar
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
            html.P("Set the number of ply",
                   style={"width": '78%', 'display': 'inline-block', 'vertical-align': 'center', "margin-bottom": "0px"}),
            dcc.Input(
                id="select_ply",
                type="number",
                debounce=True,
                min=1, max=16, step=1,
                value=default_parameters["Ply"],
                style={"width": '15%', 'display': 'inline-block', 'vertical-align': 'center'},
            ),
            html.P("Ex. 1.e4 e5 would be 2 ply",
                   style={"font-weight": "bolder", "font-size": "small", "margin": "0px"}),
            html.Hr(),
            # ----------------------------------------------------------------------------
            html.P("Set the minimum occurrences",
                   style={"width": '78%', 'display': 'inline-block', 'vertical-align': 'center'}),
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
        ],
        style=cs.SIDEBAR_STYLE,
    )

    # Main Body
    main = html.Div([
        # Top Row
        html.Div([
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
        ], style=cs.TOP_BOX),
        # 4 Mid Boxes
        html.Div([
            html.Div([
                html.P("OVERALL STATS", id="BOX1_HEADER", style=cs.BOX_HEADER),
                html.Div([html.P(id="BOX1_GAMES", children=[],
                                 style=cs.BOX1_TEXT
                                 ),
                          html.P(id="BOX1_WINS", children=[],
                                 style=cs.BOX1_TEXT
                                 ),
                          html.P(id="BOX1_LOSSES", children=[],
                                 style=cs.BOX1_TEXT
                                 ),
                          html.P(id="BOX1_DRAWS", children=[],
                                 style=cs.BOX1_TEXT
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
        ], style=cs.MIDDLE_BOX),

        # Opening Plot Area
        html.Div([
            html.Div(id='player_name_txt', children=[],
                     style={'font-size': 'xx-large',
                            'margin-top': '1rem',
                            'margin-bottom': '0.25rem'}),
            dcc.Graph(id='Opening_Map', figure={},
                      # style={'border': 'solid'}
            )
            ])
        ], style=cs.CONTENT_STYLE)

    return html.Div([sidebar, main])