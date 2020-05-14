import pandas as pd
import numpy as np
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 30)




def makeJoinPerChampTable(df_frank, df_beware, df_champions):

    df_dum = df_frank.copy()
    df_dum['numberOfGames'] = 1
    df_dum = df_dum[['championId', 'win', 'numberOfGames']]
    dict_agg = { key: 'mean' for key in df_dum.columns}
    dict_agg['numberOfGames'] = 'sum'
    dict_agg['win'] = 'mean'

    df_per_champ1 = df_dum.groupby('championId')[df_dum.columns.values].agg( dict_agg ).reset_index(drop=True)
    df_per_champ1['win'] = df_per_champ1['win'] * 100
    df_per_champ1 = df_per_champ1.round({'win': 1})
    df_per_champ1 = pd.merge( df_per_champ1, df_champions, on = 'championId', how = 'inner')
    df_per_champ1 = df_per_champ1.rename( columns = {'championId': 'championId1', 'champion': 'champion1', 'win': 'win1', 'numberOfGames': 'numberOfGames1'} )



    df_dum = df_beware.copy()
    df_dum['numberOfGames'] = 1
    df_dum = df_dum[['championId', 'win', 'numberOfGames']]

    df_per_champ2 = df_dum.groupby('championId')[df_dum.columns.values].agg( dict_agg ).reset_index(drop=True)
    df_per_champ2['win'] = df_per_champ2['win'] * 100
    df_per_champ2 = df_per_champ2.round({'win': 1})
    df_per_champ2 = pd.merge( df_per_champ2, df_champions, on = 'championId', how = 'inner')
    df_per_champ2 = df_per_champ2.rename( columns = {'championId': 'championId2', 'champion': 'champion2', 'win': 'win2', 'numberOfGames': 'numberOfGames2'} )



    df_final = pd.merge( df_per_champ1, df_per_champ2, left_on = 'championId1', right_on = 'championId2', how = 'inner')

    df_final['diff'] = df_final['win1'] - df_final['win2']
    df_final = df_final.sort_values( by = 'champion1')

    return df_final

def make_display_table(dataframe):

    df = dataframe.copy()
    df = df.drop( columns = ['championId', 'numberOfGames', 'gameCreation'] )
    df = df.rename( columns = {'kills': 'K', 'deaths': 'D', 'assists': 'A', 'totalDamageDealtToChampions': 'Damage To Champions', 'totalHeal': 'Heal'} )
    df = df.rename( columns = {'damageDealtToTurrets': 'Damage To Turrets', 'totalDamageTaken': 'Damage Taken', 'goldEarned': 'Gold'} )
    df = df.rename( columns = {'totalMinionsKilled': 'CS', 'dmgShare': 'Damage Share'} )
    df = df.rename( columns = {'champion': 'Champion', 'win': 'Win', 'largestMultiKill': 'Largest Multi Kill', 'duo': 'Duo'} )

    

    return df



def make_per_champ_display_table(dataframe):

    df = dataframe.copy()
    df = df.drop( columns = ['championId', 'item0', 'item1', 'item2','item3','item4','item5'] )
    df = df.rename( columns = {'kills': 'K', 'deaths': 'D', 'assists': 'A', 'totalDamageDealtToChampions': 'Damage To Champions', 'totalHeal': 'Heal'} )
    df = df.rename( columns = {'damageDealtToTurrets': 'Damage To Turrets', 'totalDamageTaken': 'Damage Taken', 'goldEarned': 'Gold'} )
    df = df.rename( columns = {'totalMinionsKilled': 'CS', 'dmgShare': 'Damage Share', 'numberOfGames': 'Number of Games'} )
    df = df.rename( columns = {'champion': 'Champion', 'win': 'Win Percentage', 'largestMultiKill': 'Largest Multi Kill'} )

    df['weight'] = df['Number of Games'] / df['Number of Games'].sum()

    df_dum = df.copy()
    df_dum['Champion'] = -1
    for i in range( df_dum.shape[0] ):
        
        if i == 0:
            dum_sum = df_dum.iloc[i].multiply(df_dum.iloc[i,-1])
            continue

        dum_sum = dum_sum + df_dum.iloc[i].multiply(df_dum.iloc[i,-1])

    dum_sum['Champion'] = 'all'
    df = df.append( dum_sum, ignore_index = True )
    df['Number of Games'] = df['Number of Games'].astype( int )
    df = df.drop( columns = ['weight'] )

    df = df[['Champion', 'Number of Games', 'Win Percentage','K','D', 'A', 'KDA' ,'Largest Multi Kill','Damage To Champions', 'Heal', 'Damage To Turrets', 'Damage Taken', 'Gold', 'CS', 'gameDuration', 'Damage Share']]

    return df



def get_gametime(game_time):
    day = game_time // (24 * 3600)
    game_time = game_time % (24 * 3600)
    hour = game_time // 3600
    game_time %= 3600
    minutes = game_time // 60
    game_time %= 60
    seconds = game_time
    return day, hour, minutes, seconds

def generate_markdown_for_tooltip(row):

    #no leading whitespace!

    markdown_text = '''![](http://ddragon.leagueoflegends.com/cdn/10.7.1/img/item/{}.png)
    ![](http://ddragon.leagueoflegends.com/cdn/10.7.1/img/item/{}.png)
    ![](http://ddragon.leagueoflegends.com/cdn/10.7.1/img/item/{}.png)
    ![](http://ddragon.leagueoflegends.com/cdn/10.7.1/img/item/{}.png)
    ![](http://ddragon.leagueoflegends.com/cdn/10.7.1/img/item/{}.png)
    ![](http://ddragon.leagueoflegends.com/cdn/10.7.1/img[{}.png)'''.format(row['item0'], row['item1'],row['item2'],row['item3'],row['item4'],row['item5'],)


    return markdown_text


def generate_tooltip_data(df):


    # tooltip_data = [ { c: {'type': 'markdown', 'value': generate_markdown_for_tooltip(row['item0'], row['item1'], row['item2'], row['item3'], row['item4'], row['item5']), 'delay':50, 'duration': 100000} for c,d in row.items()} for row in df.to_dict('rows')]
    tooltip_data = [ { 'Champion': {'type': 'markdown', 'value': generate_markdown_for_tooltip(row), 'delay':50, 'duration': 100000} } for row in df.to_dict('rows')]

    #outer loop (row in df.to_dict('rows')) goes over all rows 
    #inner loop ( for c,d in row.items()) goes over items in a row, where c,d of items is always column name, value
    #df to_dict gives a list of dictionaries, each dict corresponds to 1 row of the df

    #in total this is a list of dictionaries, each dict corresponding to 1 row; 
    # but each row is a dictionary of the form column_name (c): {dict describing the value of the tooltip of the corresponding cell}

    return tooltip_data


def define_variables(df_gameinfo, df_champions, summoner_name_input):

    df = df_gameinfo.copy()
    df_champions_f = df_champions.copy()


    df['KDA'] = np.where(df['deaths']>0, (df['kills'] + df['assists']) / df['deaths'], df['kills'] + df['assists'])
    df = df.round({'KDA': 1})

    df['gameCreation_dt'] = pd.to_datetime(df['gameCreation'], unit='ms') 

    df['dmgShare'] = df['dmgShare'] * 100
    df = df.round({'dmgShare': 1})

    gametime = df['gameDuration'].sum()
    day, hour, minutes, seconds = get_gametime(gametime)
    df['gameDuration'] = df['gameDuration'] / 60
    df = df.round({'gameDuration': 1})


    df['win'] = df['win'].astype(int)



    # merge with champion dataframe ---------------------------------------------------------------

    df_champions_f = df_champions_f.sort_values(by='champion')

    lst_champ_names = df_champions_f.champion.values
    df = df.merge(df_champions_f, how = 'inner', on = 'championId')

    # ------------------------------------------------------------

    column_list = ['win', 'championId', 'champion', 'kills', 'deaths', 'assists', 'item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'KDA', 'largestMultiKill', 'totalDamageDealtToChampions', 'totalHeal', 'damageDealtToTurrets', 'totalDamageTaken', 'goldEarned', 'totalMinionsKilled', 'gameDuration', 'gameCreation',  'gameCreation_dt', 'dmgShare', 'duo']
    df = df[column_list]

    df['numberOfGames'] = 1 # dummie column, dropped later


    # creating the dataframe per champ -----------------------------------------------------------------------------------------

    df_dum = df.copy()
    df_dum = df_dum.drop( columns = ['gameCreation', 'gameCreation_dt','duo'] )
    dict_agg = { key: 'mean' for key in df_dum.columns}
    dict_agg['champion'] = 'first'
    dict_agg['numberOfGames'] = 'sum'
    dict_agg['win'] = 'mean'


    df_per_champ = df_dum.groupby('championId')[df_dum.columns.values].agg( dict_agg ).reset_index(drop=True)
    df_per_champ['win'] = df_per_champ['win'] * 100
    df_per_champ = df_per_champ.round({key: 1 for key in df_per_champ.columns})

    # df_both_players = makeJoinPerChampTable(df_frank, df_beware, df_champions)

    # create the final table used for displaying and drawing -------------------------------------------------


    df = make_display_table(df)
    df_per_champ = make_per_champ_display_table(df_per_champ)
    # tooltip_data = generate_tooltip_data(df)

    # return df, gametime, lst_champ_names, df_both_players, df_per_champ, tooltip_data, day, hour, minutes, seconds
    # return df, gametime, lst_champ_names, df_per_champ, tooltip_data, day, hour, minutes, seconds
    # return df, lst_champ_names, df_per_champ, tooltip_data, day, hour, minutes, seconds
    # return df, lst_champ_names, df_per_champ, day, hour, minutes, seconds
    return df, df_per_champ, day, hour, minutes, seconds


    

# def generate_table(dataframe, max_rows=10):
#     return html.Table([
#         html.Thead(
#             html.Tr([html.Th(col) for col in dataframe.columns])
#         ),
#         html.Tbody([
#             html.Tr([
#                 html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
#             ]) for i in range(min(len(dataframe), max_rows))
#         ])
#     ])