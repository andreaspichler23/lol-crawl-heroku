import matplotlib as mpl
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib.pylab as plb
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit 
import datetime
from pandas.plotting import register_matplotlib_converters
import matplotlib.dates as mdates
register_matplotlib_converters()
import time

import requests

# account_id = 'vrYTiexpWDh_8et0s2ay4unXtfBu-m0P3I3e3g-ZbZ3ibg' #frank
# summoner_id = 'oS992syEwEl4RHwId4maA_Voz_uhvpk3BszwUiASzjEeXQ0' #frank
# summoner_name_global = 'Frank Drebin'

api_key = 'RGAPI-1511c5f9-3875-4d70-a7d6-374e6c31cba4'

account_id = 'REwF0pRNRdEV0MCSVwEYBSwGy1s6jeEw3l7U39wg1oVQug' #beware
summoner_id = 'zI2FIMMuLs4IEYsaOm6zsLDmW2797EBBPw5jVN_UAswPUwI' #beware
summoner_name_global = 'bewareoftraps'

    

def matchlist_url_maker(api_key, account_id, queue, beginIndex, endIndex):
    url = "https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/"
    url += account_id + '?'
    url += 'queue=' + str(queue) + '&'
    url += 'beginIndex=' + str(beginIndex)  + '&'
    url += 'endIndex=' + str(endIndex)  + '&'
    url += 'api_key=' + api_key 

    return url

def game_url_maker(api_key, game_id):
    url = 'https://euw1.api.riotgames.com/lol/match/v4/matches/'
    url += str(game_id) + '?'
    url += 'api_key=' + api_key

    return url

def get_match_list(account_id):

    url = matchlist_url_maker(api_key, account_id, 450, 0, 5)
    # fail_count = 0
    
        
    response = requests.get(url)
    match_dict = response.json()['matches'] #list of dicts corresponding to matches
    df_matchlist = pd.DataFrame.from_dict(match_dict)

        
    # time.sleep(1)
    # fail_count += 1
    # if fail_count == 10:
    #     df_matchlist = pd.DataFrame()
    #     break
    # continue
        
           
    # print(df_match.columns)

    # for i in range(100000):
    #     beginIndex = (i+1)*100
    #     url = matchlist_url_maker(api_key, account_id, 450, beginIndex)
    #     response = requests.get(url)
    #     match_dict = response.json()['matches']
    #     if len(match_dict) == 0:
    #         break
    #     # df_dum = pd.DataFrame.from_dict(match_dict)
    #     df_matchlist = df_matchlist.append(pd.DataFrame.from_dict(match_dict))


    return df_matchlist

def get_participant_id(list_identities):

    for i in range(len(list_identities)):

        str_summoner_name = list_identities[i]['player']['summonerName']
        if str_summoner_name == summoner_name_global:
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



def get_player_game_info(api_key, game_id): #, player_id

    url = game_url_maker(api_key, game_id)
    # print(url)
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
    list_data_all_players_one_game = []

    for player_id in range(1,11):
        my_id = player_id
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
        list_data_all_players_one_game.append(dict_player)

    list_account_ids =  [ list_identities[i]['player']['accountId'] for i in range(10) ]

    df_1_game = pd.DataFrame.from_dict(list_data_all_players_one_game)
    
    return df_1_game, list_account_ids



def get_player_info(df_matchlist):

    # list_player_info = []
    matchlist = df_matchlist['gameId'].to_numpy()
    counter = 0
    for game_id in matchlist:
        counter += 1
        # print(counter, game_id)
        df_1_game, list_account_ids = get_player_game_info(api_key, game_id) #, player_id
        time.sleep(1.3)
        if counter == 1:
            df_gameinfo = df_1_game
            continue
        df_gameinfo = df_gameinfo.append(df_1_game, ignore_index = True)
       
        # if counter == 2:
        #     break
    
    # df_gameinfo = pd.DataFrame.from_dict(list_player_info)
    
    return df_gameinfo, list_account_ids


for i in range(2000):
    print('account id:', account_id)
    print('summoner number:', i)
    while True:
        try:
            df_matchlist = get_match_list( account_id )
            df_matchlist['time'] = pd.to_datetime(df_matchlist['timestamp'], unit='ms') 
        except:
            while True:
                j = np.random.randint(0,10)
                new_account_id = list_account_ids[j]
                if new_account_id != account_id:
                    account_id = new_account_id
                    break
            continue
        else:
            df_gameinfo_dum, list_account_ids = get_player_info( df_matchlist )
            while True:
                j = np.random.randint(0,10)
                new_account_id = list_account_ids[j]
                if new_account_id != account_id:
                    account_id = new_account_id
                    break
            break
   
    print('shape of dataframe of this game:', df_gameinfo_dum.shape)
    if i == 0:
        df_gameinfo = df_gameinfo_dum
        continue
    df_gameinfo = df_gameinfo.append(df_gameinfo_dum, ignore_index = True)
    print('shape of total dataframe:', df_gameinfo.shape)




df_gameinfo.to_csv('C:/Users/U2JD7FU/Desktop/Private/Programmieren/Python/Lol/game-data.csv')
df_gameinfo.to_excel('C:/Users/U2JD7FU/Desktop/Private/Programmieren/Python/Lol/game-data.xlsx')


print(df_gameinfo.columns)
print(df_gameinfo.shape)

