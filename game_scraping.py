# import matplotlib as mpl
# import statsmodels.api as sm
# import matplotlib.pyplot as plt
# import matplotlib.pylab as plb
import numpy as np
import pandas as pd
# from scipy.optimize import curve_fit 
import datetime
# from pandas.plotting import register_matplotlib_converters
# import matplotlib.dates as mdates
# register_matplotlib_converters()
import time

import requests

# account_id = 'vrYTiexpWDh_8et0s2ay4unXtfBu-m0P3I3e3g-ZbZ3ibg' #frank
# summoner_id = 'oS992syEwEl4RHwId4maA_Voz_uhvpk3BszwUiASzjEeXQ0' #frank
# summoner_name_global = 'Frank Drebin'

api_key = 'RGAPI-a297908e-4a42-4ce7-9465-ae0bb56e5ff7'

# account_id = 'REwF0pRNRdEV0MCSVwEYBSwGy1s6jeEw3l7U39wg1oVQug' #beware
# summoner_id = 'zI2FIMMuLs4IEYsaOm6zsLDmW2797EBBPw5jVN_UAswPUwI' #beware
# summoner_name_global = 'bewareoftraps'

#  https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/bewareoftraps

def get_account_id(summoner_name, api_key):

    summoner_name = summoner_name.replace(' ', '%20')
    url = 'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + summoner_name
    url += '?api_key=' + api_key
    response = requests.get(url)
    account_id = response.json()['accountId']
    return account_id


def matchlist_url_maker(api_key, account_id, queue, beginIndex):
    url = "https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/"
    url += account_id + '?'
    url += 'queue=' + str(queue) + '&'
    url += 'beginIndex=' + str(beginIndex)  + '&'
    url += 'api_key=' + api_key 
      
    return url

def game_url_maker(api_key, game_id):
    url = 'https://euw1.api.riotgames.com/lol/match/v4/matches/'
    url += str(game_id) + '?'
    url += 'api_key=' + api_key

    return url

def get_match_list(account_id):
    url = matchlist_url_maker(api_key, account_id, 450, 0)
    response = requests.get(url)
    match_dict = response.json()['matches'] #list of dicts corresponding to matches
    df_matchlist = pd.DataFrame.from_dict(match_dict)
    # print(df_match.columns)

    for i in range(100000):
        beginIndex = (i+1)*100
        url = matchlist_url_maker(api_key, account_id, 450, beginIndex)
        response = requests.get(url)
        match_dict = response.json()['matches']
        if len(match_dict) == 0:
            break
        # df_dum = pd.DataFrame.from_dict(match_dict)
        df_matchlist = df_matchlist.append(pd.DataFrame.from_dict(match_dict))


    return df_matchlist

def get_participant_id(list_identities, account_id):

    for i in range(len(list_identities)):

        str_account_id = list_identities[i]['player']['accountId']
        # print(str_summoner_name)
        if str_account_id == account_id:
            my_id = i+1
            break

    return my_id


def get_team_dmg(response):

    team_1_dmg = 0
    team_2_dmg = 0
    for participant in range(1,6):
        team_1_dmg += response.json()['participants'][participant-1]['stats']['totalDamageDealtToChampions']

    for participant in range(6,11):
        team_2_dmg += response.json()['participants'][participant-1]['stats']['totalDamageDealtToChampions']

    return team_1_dmg, team_2_dmg


def get_duo(response):

    we_count = 0
    for id in range(10):
        try:
            curr_name = response.json()['participantIdentities'][id]['player']['summonerName']
        except:
            continue
        if (curr_name == 'bewareoftraps') | (curr_name == 'Frank Drebin'):
            we_count += 1
    # print(we_count)
    duo = int(we_count/2)

    return duo


def get_player_game_info(api_key, game_id, account_id):

    url = game_url_maker(api_key, game_id)
    while True:
        try:
            response = requests.get(url)
            list_identities = response.json()['participantIdentities']
        except:
            print('exception occured')
            time.sleep(1)
            continue
        else:
            break
    
    my_id = get_participant_id(list_identities, account_id)
    dict_player = response.json()['participants'][my_id-1]['stats']
    dict_player['gameDuration'] = response.json()['gameDuration']
    dict_player['gameCreation'] = response.json()['gameCreation']
    dict_player['championId'] = response.json()['participants'][my_id-1]['championId']
    dict_player['gameId'] = response.json()['gameId']
    teamId = response.json()['participants'][my_id-1]['teamId']
    dict_player['teamId'] = teamId

    team_1_dmg, team_2_dmg = get_team_dmg(response)
    dict_player['team1dmg'] = team_1_dmg
    dict_player['team2dmg'] = team_2_dmg
    dmg_dealt = response.json()['participants'][my_id-1]['stats']['totalDamageDealtToChampions']

    dmg_share = 0
    if teamId == 100:
        dmg_share = dmg_dealt/team_1_dmg
    if teamId == 200:
        dmg_share = dmg_dealt/team_2_dmg
    dict_player['dmgShare'] = dmg_share

    dict_player['duo'] = get_duo(response)
    
    return dict_player



def get_player_info(df_matchlist, account_id):

    list_player_info = []
    matchlist = df_matchlist['gameId'].to_numpy()
    counter = 0
    for game_id in matchlist:
        counter += 1
        print(counter, game_id)
        dict_player = get_player_game_info(api_key, game_id, account_id)
        list_player_info.append(dict_player)
        time.sleep(1.3)
        # if counter == 20:
        #     break

    df_gameinfo = pd.DataFrame.from_dict(list_player_info)
    
    return df_gameinfo
    
def main(summoner_name, api_key):

    if summoner_name == 'bewareoftraps':
        df_gameinfo = pd.read_csv('game-data_beware.csv')
    elif summoner_name == 'Frank Drebin':
        df_gameinfo = pd.read_csv('game-data_frank.csv')
    else:
        account_id = get_account_id(summoner_name, api_key)
        df_matchlist = get_match_list(account_id)
        df_matchlist['time'] = pd.to_datetime(df_matchlist['timestamp'], unit='ms') 
        df_gameinfo = get_player_info( df_matchlist, account_id )

        summoner_name = summoner_name.replace(' ', '%20')
        filename = summoner_name + '.csv'
        df_gameinfo.to_csv(filename)

    return df_gameinfo



# summoner_name = 'Crudelmudel'
# main(summoner_name, api_key)

# df_gameinfo.to_csv('C:/Users/U2JD7FU/Desktop/Private/Programmieren/Python/Lol/game-data.csv')
# df_gameinfo.to_excel('C:/Users/U2JD7FU/Desktop/Private/Programmieren/Python/Lol/game-data.xlsx')


# print(df_gameinfo.columns)
# print(df_gameinfo.shape)

