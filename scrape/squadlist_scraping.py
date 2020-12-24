import requests
from bs4 import BeautifulSoup
from scrape import database

links = list(database.teams.keys())

with open('player_list.txt', 'w', encoding='utf-8') as out:
    for link in links:
        r = requests.get(link)
        source = BeautifulSoup(r.content, 'html.parser').find_all('tr', attrs={'class': 'p0c-team-squad__row'})
        for x in source:
            player = x.find('a', attrs={'class': 'p0c-team-squad__player-name'}).text.strip()
            out.write(f"'{player}': '-',\n")
        out.write('\n')
