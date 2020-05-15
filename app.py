import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State
import plotly.express as px


import import_func
import game_scraping

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 20)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# external_stylesheets = ['C:/Users/U2JD7FU/Desktop/Private/Programmieren/Python/Lol/style.css']


column_list = ['item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'Win', 'Champion','K','D', 'A', 'KDA' ,'Largest Multi Kill','Damage To Champions', 'Heal', 'Damage To Turrets', 'Damage Taken', 'Gold', 'CS', 'gameDuration', 'gameCreation_dt', 'Damage Share']
column_list_per_champ = ['Champion', 'Number of Games', 'Win Percentage','K','D', 'A', 'KDA' ,'Largest Multi Kill','Damage To Champions', 'Heal', 'Damage To Turrets', 'Damage Taken', 'Gold', 'CS', 'gameDuration', 'Damage Share']



df_champions = pd.read_csv('champions.csv')
df_total_per_champ = pd.read_csv('champions_mean.csv')
df_total_per_champ = df_total_per_champ.drop( columns = ['Unnamed: 0'] )
df_total_per_champ = import_func.make_per_champ_display_table(df_total_per_champ)

# columns_list_both_players = ['championId1', 'champion1', 'win1', 'numberOfGames1', 'championId2', 'champion2', 'win2', 'numberOfGames2']
# df_both_players = pd.DataFrame(columns = columns_list_both_players)

api_key = 'RGAPI-2fec44d3-8b38-438d-8fda-a5409d8bab55'

df_frank = pd.read_csv('game-data_frank.csv')
df_beware = pd.read_csv('game-data_beware.csv')



app = dash.Dash(__name__, external_stylesheets=external_stylesheets) 

server = app.server

app.layout = html.Div( children = [

    dcc.Store(
        id = 'store_per_champ_table'
    ),

    dcc.Store(
        id = 'store_main_table'
    ),

    html.Div( style = {'padding': 20} ),

    html.Div( 
        children = [

            dcc.Input(
                id = 'summoner_name_input',
                type = 'text',
                style={
                    'textAlign': 'center'
                },
                placeholder='Summoner Name'
            ),

            html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
        ],
        style=dict(display='flex', justifyContent='center')
        
    ),

    html.Div( style = {'padding': 50} ),


    html.H1(
        # children= 'Hello '+ summoner_name + '!',
        className='test',
        style={
            'textAlign': 'center',
            'color': 'red' ##7FDBFF
        },
        id = 'welcome_message'
    ),

    html.H2(
        style={
            'textAlign': 'center',
            'color': '#7FDBFF'
        },
        id = 'wasted_message'
    ),


    dcc.Dropdown(
        id='champ_sel_dropdown',
        # options=[
        #     {'label': champ, 'value': champ} for champ in df_champions.champion.unique()
        # ],
    ),

    html.Img(
        id = 'img_champ_summary',
        # className = 'img-class'
    ),

    dcc.Graph(id = 'spider_web_graph'),

    dcc.Markdown(
        id = 'text_summary',
        style={'columnCount': 3}
    ),

    html.Div( style = {'padding': 50} ),

    html.H5( children = 'A sortable table of all the ARAM games you played in the last 2 years. Hover over the champion name to see the items you bought!' ),

    dash_table.DataTable(
        id='main_table',
        # columns= [ {"name": 'item0', "id": 'item0', 'type': 'text', 'presentation': 'markdown'} ] + [{"name": i, "id": i} for i in df.columns if i != 'item0'],
        # css=[
        #     dict(selector='td table', rule='height: 64px;'),
        # ],
        sort_action='custom',
        sort_mode='single',
        sort_by=[],
        style_table={
            'maxHeight': '500px',
            'overflowY': 'scroll',
        },
        # style_cell={'height': '64px'},
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{Win} eq 0'
                },
                'backgroundColor': 'rgba(255,0,0,0.3)',
            },
            {
                'if': {
                    'filter_query': '{Win} eq 1'
                },
                'backgroundColor': 'rgba(0,0,255,0.3)',
            }
        ]
        # fixed_rows={ 'headers': True, 'data': 0 },
        # style_cell={'width': '100px'},
    ),


    html.Div( style = {'padding': 50} ),
    html.H5( children = 'A graph of all the ARAM games you played in the last 2 years. Each point corresponds to 1 game. Hover over points to see more info' ),


    html.Div( children = [

        html.Label('X Axis Input',
            style= {
                'textAlign': 'center',
            }
        ),

        dcc.Dropdown(
            id='main_graph_x_axis',
            options=[
                {'label': column, 'value': column} for column in column_list
            ],
            value='gameDuration'
        ),

        html.Label('Y Axis Input',
            style= {
                'textAlign': 'center',
            }
        ),

        dcc.Dropdown(
            id='main_graph_y_axis',
            options=[
                {'label': column, 'value': column} for column in column_list
            ],
            value='Damage To Champions'
        ),

        html.Label('Color Input',
            style= {
                'textAlign': 'center',
            }
        ),

        dcc.Dropdown(
            id='main_graph_color',
            options=[
                {'label': column, 'value': column} for column in column_list
            ],
            value='Win'
        ),

        html.Label('Size Input',
            style= {
                'textAlign': 'center',
            }
        ),

        dcc.Dropdown(
            id='main_graph_size',
            options=[
                {'label': column, 'value': column} for column in column_list
            ],
            value='Largest Multi Kill'
        ),

    ], style={'columnCount': 2} ),

    dcc.Graph(id = 'main_graph'),

    html.Div( style = {'padding': 50} ),

    html.H2(
        children= 'Per Champion averages',
        style={
            'textAlign': 'center',
            'color': '#7FDBFF'
        }
    ),

    html.H5( children = '''This section tells you how good you do on each champion. 
                            Please select how many games you need to have played with each champion to be taken into account in the following analysis:''' ),


    dcc.Slider(
        id='min_num_games_slider',
        # min=1,
        # max=10 if df_per_champ.empty else df_per_champ['Number of Games'].max(),
        value=1,
        # marks={str(num): str(num) for num in range(1, 10) if df_per_champ.empty else str(num): str(num) for num in range(1, df_per_champ['Number of Games'].max() ) }, # df_per_champ['Number of Games'].max()
        step=None
    ),

    dash_table.DataTable(
        id='table_per_champ',
        columns=[{"name": i, "id": i} for i in column_list_per_champ],
        # data=df_per_champ.to_dict('records'),
        sort_action='native',
        # filter_action='native',
        style_table={
            'maxHeight': '500px',
            'overflowY': 'scroll'
        },
        # fixed_rows={ 'headers': True, 'data': 0 },
        # style_cell={'width': '100px'},
    ),

    html.Div( style = {'padding': 30} ),


    html.H5( children = 'A graph of all champions you played enough games. Each data point represents your average performance on a champion' ),

    dcc.Graph(id = 'per_champ_graph',
    ),

    html.H5( children = 'A graph of the average ARAM performance of all the champions in LOL' ),

    dcc.Graph(id = 'per_champ_graph_total',
    ),

    # dcc.Graph(
    #     id = 'per_champ_bar_graph',
    # ),
    
    # dcc.Graph(id = 'graph_player_comparison',
    # ),

])

@app.callback(
    [Output('min_num_games_slider', 'marks'),
    Output('min_num_games_slider', 'min'),
    Output('min_num_games_slider', 'max')],
    [Input('store_per_champ_table', 'data')]
    )
def update_slider_marks(dict_per_champ):


    df_per_champ_slider = pd.DataFrame.from_dict(dict_per_champ)
    if df_per_champ_slider.empty:
        markings={str(num): str(num) for num in range(1,   10) }
        maxi = 10
    else:
        
        maxi = int(df_per_champ_slider['Number of Games'].max())
        markings={str(num): str(num) for num in range(1,   maxi) }

    mini = 1


    return markings, mini, maxi


@app.callback(
    Output('text_summary', 'children'),
    [Input('champ_sel_dropdown', 'value'),
    Input('store_per_champ_table', 'data'),
    Input('store_main_table', 'data'),
    ] )  
def update_summary(champ_name, dict_per_champ, dict_main):

    df5 = pd.DataFrame.from_dict(dict_main)
    df_per_champ2 = pd.DataFrame.from_dict(dict_per_champ)


    if champ_name is not None:
        df5 = df5.loc[ df5['Champion'] == champ_name ]
        df_per_champ2 = df_per_champ2.loc[ df_per_champ2['Champion'] == champ_name ]
        n_games = df_per_champ2['Number of Games'].values
        n_games = n_games[0]
    else:
        n_games = df_per_champ2['Number of Games'].sum()

    winrate = np.around(100 * df5['Win'].mean(),1)
    avg_kda = np.around(df5['KDA'].mean(),1)
    dmg_share = np.around(df5['Damage Share'].mean(),1)
    avg_kills = np.around(df5['K'].mean(),1)
    avg_deaths = np.around(df5['D'].mean(),1)
    avg_assists = np.around(df5['A'].mean(),1)
    avg_cs = np.around(df5['CS'].mean(),1)


    markdown_text = '''
    ## Winrate = {} %
    ## Number of Games = {}
    ## Average Damage Share = {} %
    ## Average KDA = {}
    ## Average Kills = {}
    ## Average Deaths = {}
    ## Average Assists = {}
    ## Average CS = {}

    '''.format(winrate, n_games, dmg_share, avg_kda, avg_kills, avg_deaths, avg_assists, avg_cs) #, champ_name, string_img

    if df5.empty:
        markdown_text = '''
            ## Winrate = 
            ## Number of Games = 
            ## Average Damage Share = 
            ## Average KDA = 
            ## Average Kills = 
            ## Average Deaths = 
            ## Average Assists = 
            ## Average CS =
            '''

    return markdown_text


    
# ----------------------------------------------------------------------------------------

@app.callback(
    Output('img_champ_summary', 'src'),
    [Input('champ_sel_dropdown', 'value'), 
    ] )  
def update_img(champ_name):



    if champ_name is not None:
        string_img = 'http://ddragon.leagueoflegends.com/cdn/10.7.1/img/champion/' + champ_name + '.png'
    else:
    #     string_img = 'http://ddragon.leagueoflegends.com/cdn/6.8.1/img/map/map12.png'
        string_img = ''

    return string_img

# -----------------------------------------------------------------------------------------

@app.callback(
    Output('per_champ_graph', 'figure'),
    [Input('min_num_games_slider', 'value'),
    Input('store_per_champ_table', 'data')
    ] )  
def update_graph(min_num, dict_per_champ):

    df1 = pd.DataFrame.from_dict(dict_per_champ)
    df1 = df1.loc[ df1['Number of Games'] >= min_num ]
    df1 = df1.loc[ df1['Champion'] != 'all' ]
    if df1.empty:
        fig = px.scatter()
    else:
        fig = px.scatter(df1, x  = 'Win Percentage', y = 'KDA', color = 'Damage Share', hover_data=['Champion', 'Damage Share'], size= 'Number of Games')
    return fig


# -----------------------------------------------------------------------------------------

@app.callback(
    Output('per_champ_graph_total', 'figure'),
    [Input('min_num_games_slider', 'value')] )  
def update_graph_total(min_num):


    df_1 = df_total_per_champ.copy()
    # df1 = df_per_champ.loc[ df_per_champ['Number of Games'] > min_num ]
    fig = px.scatter(df_1, x  = 'Win Percentage', y = 'KDA', color = 'Damage Share', hover_data=['Champion', 'Damage Share'], size= 'Number of Games')
    return fig


# ----------------------------------------------------------------------------------------------

@app.callback(
    Output('table_per_champ', 'data'),
    [Input('min_num_games_slider', 'value'),
    Input('store_per_champ_table', 'data')
    ] )  
def update_per_champ_table(min_num, dict_per_champ):

    df7 = pd.DataFrame.from_dict(dict_per_champ)
    df7 = df7.loc[ df7['Number of Games'] >= min_num ]
    df7 = df7.loc[ df7['Champion'] != 'all' ]


    data_dict = df7.to_dict('rows')

    return data_dict

# ----------------------------------------------------------------------

# @app.callback(
#     Output('graph_player_comparison', 'figure'),
#     [Input('min_num_games_slider', 'value'),
#     Input('refresh-button-state', 'n_clicks')] )  
# def update_graph3(min_num, n_clicks):

#     df4 = df_both_players.copy()
#     df4 = df4.loc[ (df4['numberOfGames1'] > min_num) & (df4['numberOfGames2'] > min_num) ]
#     if df4.empty:
#         fig = px.scatter()
#     else:
#         fig = px.scatter(df4, x='champion1', y='diff', hover_data=['champion1'], color = 'win1')

#     return fig

# ---------------------------------------------------

@app.callback(
    [Output('main_table', 'data'),
    Output('main_table', 'tooltip_data'),
    Output('main_table', 'columns')
    ],
    [Input('champ_sel_dropdown', 'value'),
    Input('main_table', 'sort_by'),
    Input('store_main_table', 'data'),
    ] )  
def update_table(champ_name, sort_by, dict_main):

    df2 = pd.DataFrame.from_dict(dict_main)

    if champ_name is not None:
        df2 = df2.loc[ df2['Champion'] == champ_name ]

    if df2.empty:
        data_dict = {}
    else: 
        if len(sort_by):
            df2 = df2.sort_values(
                by = sort_by[0]['column_id'],
                ascending=sort_by[0]['direction'] == 'asc',
            )
        else:
            # No sort is applied
            df2 = df2

        df2['gameCreation_dt'] = pd.to_datetime(df2['gameCreation_dt'], infer_datetime_format=True) 
        df2['gameCreation_dt'] = df2['gameCreation_dt'].dt.strftime('%d/%m/%Y %H:%M')

    tooltip_data = import_func.generate_tooltip_data(df2)

    df2 = df2.drop( columns = ['item0', 'item1', 'item2', 'item3', 'item4', 'item5'] )

    columns= [{"name": i, "id": i} for i in df2.columns]

    data_dict = df2.to_dict('records')

    return data_dict, tooltip_data, columns

# -----------------------------------------------------

@app.callback(
    Output('main_graph', 'figure'),
    [Input('champ_sel_dropdown', 'value'),
     Input('main_graph_x_axis', 'value'),
     Input('main_graph_y_axis', 'value'),
     Input('main_graph_color', 'value'),
     Input('main_graph_size', 'value'),
     Input('store_main_table', 'data'),
      ] )
def update_graph2(champ_name, x_axis_name, y_axis_name, color_name, size_name, dict_main):
    
    df3 = pd.DataFrame.from_dict(dict_main)
    if champ_name is not None:
        df3 = df3.loc[ df3['Champion'] == champ_name ]
    if df3.empty:
        fig = px.scatter()
    else:
        fig = px.scatter(df3, x  = x_axis_name, y = y_axis_name, color = color_name, hover_data=['Champion', 'Damage Share'], size= size_name)

    return fig

 # -----------------------------------------------------

@app.callback(
    Output('spider_web_graph', 'figure'),
    [Input('champ_sel_dropdown', 'value'),
    Input('store_per_champ_table', 'data')
    ] ) 
def update_spider_graph(champ_name, dict_per_champ):

    df_total_per_champ_1 = df_total_per_champ.copy()
    df_per_champ_1 = pd.DataFrame.from_dict(dict_per_champ)

    if champ_name is not None:
        df_total_per_champ_1 = df_total_per_champ_1.loc[ df_total_per_champ_1['Champion'] == champ_name ]
        df_per_champ_1 = df_per_champ_1.loc[ df_per_champ_1['Champion'] == champ_name ]
    else:
        df_total_per_champ_1 = df_total_per_champ_1.loc[ df_total_per_champ_1['Champion'] == 'all' ]
        df_per_champ_1 = df_per_champ_1.loc[ df_per_champ_1['Champion'] == 'all' ]


    if df_per_champ_1.empty:
        fig = px.line_polar()
    else:
        df_total_per_champ_1 = df_total_per_champ_1.drop( columns = ['Champion', 'Number of Games'] )
        df_per_champ_1 = df_per_champ_1.drop( columns = ['Champion', 'Number of Games'] )

        lst_div = [ a/b for (a,b) in zip(df_per_champ_1.iloc[0], df_total_per_champ_1.iloc[0]) ]
        lst_final = [ {'r': value1, 'theta': value2} for (value1, value2) in zip(lst_div, df_per_champ_1.columns) ]
        df_final = pd.DataFrame.from_dict(lst_final)

        axis_min = np.min( np.array( (0.5, np.min(lst_div)) ) )
        axis_max = np.max( np.array( (1.3, np.max(lst_div)) ) )

        fig = px.line_polar(df_final, r='r', theta='theta', line_close=True)
        fig.update_layout(
            polar = dict(
                radialaxis_range = [axis_min, axis_max]
            )
        )
        # fig.update_traces(fill='toself')
    return fig

# -------------------------------------------------------------------------

@app.callback( [Output('welcome_message', 'children'),
                Output('wasted_message', 'children'),
                Output('champ_sel_dropdown', 'options'),
                Output('store_per_champ_table', 'data'),
                Output('store_main_table', 'data')
                ],
              [Input('submit-button-state', 'n_clicks')],
              [State('summoner_name_input', 'value')]  )
def update_output(n_clicks, summoner_name_input):

    day, hour, minutes, seconds = 0, 0, 0, 0
    df_gameinfo = pd.DataFrame()
    df = pd.DataFrame(columns = column_list)
    df_per_champ = pd.DataFrame(columns = column_list_per_champ)


    if summoner_name_input is not None:
        df_gameinfo = game_scraping.main(summoner_name_input, api_key, df_frank, df_beware)
        df, df_per_champ, day, hour, minutes, seconds = import_func.define_variables(df_gameinfo, df_champions, summoner_name_input)
        df = df.sort_values( by = 'Champion' )

    if summoner_name_input is not None:
        return1 = 'Hello '+ str(summoner_name_input) + '!'
    else:
        return1 = 'Hello summoner!'
    return2 = 'You wasted ' + str(day) + ' days ' + str(hour) + ' hours ' + str(minutes) + ' minutes ' + str(seconds) + ' seconds on ARAM in the last 2 years'
    if df.empty:
        return3 = list()
    else:
        return3 = [ {'label': champ, 'value': champ} for champ in df.Champion.unique() ]

    dict_per_champ = df_per_champ.to_dict()
    dict_main = df.to_dict()

    return return1, return2, return3, dict_per_champ, dict_main 



if __name__ == '__main__':
    app.run_server(debug=True)