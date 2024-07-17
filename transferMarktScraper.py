import re
import requests
import pandas as pd
import time

from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

#Creating a web scraper that is capable of iterating through potential USMNT players and logging their weekly performance data
#Basis of the code comes from McKay Johns video: https://www.youtube.com/watch?v=cBVVRQG6eak

#Finding Player Information using CSS Selectors and RegEx
def playerInformation(player_name,id):

    cur_url = f'https://www.transfermarkt.us/{player_name}/profil/spieler/{id}'
    response = requests.get(cur_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    #Main Player Page
    player_name = soup.select_one('h1[class="data-header__headline-wrapper"]').text.split('\n')[-1].strip()
    player_age = \
    soup.select_one('span[itemprop="birthDate"]').text.split('\n')[-1].strip().replace('(', '').replace(')', '').split(
        ' ')[-1]
    club = soup.select_one('span[class="data-header__club"]').text.split('\n')[-1].strip()
    position = re.search("<dd class=\"detail-position__position\">(.*)</dd>", str(soup)).group(1).strip()

    player_information = [player_name, player_age, club, position]
    return(player_information)

#Finding Season Performance Information using RegEx
def playerSeasonPerformance(player_name,id):

    # Current Season Stats
    cur_url = f"https://www.transfermarkt.us/{player_name}/leistungsdaten/spieler/{id}/plus/0?saison=2023"
    response = requests.get(cur_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    #Table format = Appearances, goals, assists, yellows, second yellows, red, total minutes
    player_season_performance_list = re.search("Total  23/24:.*?\"zentriert\">(.*)</td></tr>", str(soup)).group(1).replace('-','0').replace('</td><td','').replace('class="zentriert">','').replace('class="rechts">','').replace('\'','').replace('.','').split(' ')
    player_season_performance_int =[eval(i) for i in player_season_performance_list]

    #Adding column for goal contributions per 90
    player_season_performance_int.append(round((sum(player_season_performance_int[1:3])*90/(player_season_performance_int[-1])),2))
    player_season_performance=player_season_performance_int

    return(player_season_performance)

# pd.DataFrame

if __name__ == '__main__':
    player_name = ['Christian Pulisic','Weston McKennie','Timothy Weah']
    player_id =['315779','332697','370846']

    # player_name =['Christian Pulisic']
    # player_id =['315779']

    player_df = pd.DataFrame(columns = ['Name','Age','Club','Position','Appearances','Goals','Assists','Yellows','Second Yellows','Reds','Goal Contribution per 90','Total Minutes'])

    #iterate through player name list and replace spaces with Hyphen?
    player_hyphen = [i.replace(' ','-') for i in player_name]

    for i in range(0,len(player_name)):
        player_information = playerInformation(player_hyphen[i],player_id[i])
        player_season_performance = playerSeasonPerformance(player_hyphen[i],player_id[i])

        player_list_comb = player_information + player_season_performance
        player_df.loc[i]=player_list_comb
        time.sleep(5)

print(player_df)