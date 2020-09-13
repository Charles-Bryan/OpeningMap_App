import dash_core_components as dcc
import dash_html_components as html

from assets.src import css_styles as cs
from assets.src.openings import opening_options


def setup_layout(app):
    # App layout
    sidebar = html.Div(
        [
            html.P("OpeningMap", style={'text-align': 'left',
                                        'font-size': '1.7em',
                                        'font-family': 'Acumin, "Helvetica Neue", sans-serif',
                                        'color': '#0000ff',
                                        'font-weight': '300',
                                        'vertical-align': 'top',
                                        'margin': '0',
                                        'margin-bottom': '2rem',
                                        }),
            html.H2("Search Settings", className="display-4", style={'text-align': 'center', 'font-size': '2em'}),
            html.Hr(),

            html.P("Enter a Lichess username", className="lead"),
            dcc.Input(id="input_PlayerName", type="text", value="E4_is_Better", placeholder="E4_is_Better",
                      style={'margin-right': '1rem',}),
            html.Button('Submit', id='submit-val', n_clicks=0, style={"background-color": "darkgray"}),
            html.Hr(),

            html.P("Which color pieces?", className="lead"),
            dcc.RadioItems(
                id="select_PlayerColor",
                options=[
                    {'label': 'White', 'value': 'White'},
                    {'label': 'Black', 'value': 'Black'}
                ],
                value='Black',
                labelStyle={'display': 'inline-block'}),
            html.Hr(),

            html.P("Which time controls?", className="lead"),
            dcc.Checklist(
                id="select_GameTypes",
                options=[
                    {'label': 'Rapid', 'value': 'rapid_True'},
                    {'label': 'Classical', 'value': 'classical_True'}
                ],
                value=['rapid_True', 'classical_True']
            ),
            html.Hr(),

            html.P("Choose an Opening (optional)", className="lead"),
            dcc.Dropdown(id="select_opening",
                         options=opening_options,
                         multi=False,
                         value="All Games",
                         style={'width': "100%"}
                         ),
            html.Hr()
        ],
        style=cs.SIDEBAR_STYLE,
    )

    main = html.Div([
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
                    html.H1("OpeningMap", style={'text-align': 'center'}),
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
        html.Div([
            html.Div([html.P("BOX1", style={'text-align': 'left'})], style=cs.MID_BOXES),
            html.Div([html.P("BOX2", style={'text-align': 'left'})], style=cs.MID_BOXES),
            html.Div([html.P("BOX3", style={'text-align': 'left'})], style=cs.MID_BOXES),
            html.Div([html.P("BOX4", style={'text-align': 'left'})], style=cs.MID_BOXES),
        ], style=cs.MIDDLE_BOX),
        html.Div([
            html.Div(id='my_text', children=[]),  # Display Text
            html.Br(),  # Line Break
            dcc.Graph(id='Opening_Map', figure={}),
            ])
        ], style=cs.CONTENT_STYLE)

    return html.Div([sidebar, main])