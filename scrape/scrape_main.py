import requests
from bs4 import BeautifulSoup
from scrape import database

# Mackolik links and Whoscored Predictions
teams = database.teams

# Position data from POSosyal directly
positions = database.positions

gk_data = {}
d_data = {}
m_data = {}
st_data = {}

# Scraping
playerCount = 0
karagumrukBye = kasimpasaBye = False
if teams['https://www.mackolik.com/takim/karag%C3%BCmr%C3%BCk/kadro/c3txoz57mu7w9y1jprvnv2flr/s%C3%BCper-lig/2020-2021/'] == (None, None):
    karagumrukBye = True
if teams['https://www.mackolik.com/takim/kas%C4%B1mpa%C5%9Fa/kadro/4idg23egrrvtrbgrg7p5x7bwf/s%C3%BCper-lig/2020-2021/'] == (None, None):
    kasimpasaBye = True

yusuferdogan = ' KARAGUMRUK'
for team in teams.items():
    link = team[0]
    sp, cp = team[1]
    r = requests.get(link)
    source = BeautifulSoup(r.content, 'html.parser').find_all('tr', attrs={'class': 'p0c-team-squad__row'})

    if sp is None and cp is None:  # If the team is not playing this week
        continue

    for x in source:
        player = x.find('a', attrs={'class': 'p0c-team-squad__player-name'}).text.strip()
        if player == 'Yusuf Erdoğan':  # Because there are 2 different Yusuf Erdogans in the league, the name of the player's team is appended to the string.
            if karagumrukBye and kasimpasaBye:
                print('Yusuf Erdogan error')
                continue
            elif karagumrukBye:
                player += ' KASIMPASA'
            elif kasimpasaBye:
                player += ' KARAGUMRUK'
            else:
                player += yusuferdogan
                yusuferdogan = ' KASIMPASA'

        try:  # Some youth players seem to exist on the Mackolik source code but not in the real site. This is not a big deal as these players don't play in the league anyway.
            temp = positions[player]
            if isinstance(temp, str):
                pos = positions[player]
                penaltyGoals = '-'
            else:
                pos, penaltyGoals = positions[player]

        except KeyError:
            print('Player not found: ' + player)
            continue

        if pos == '-':  # If the player isn't in the predicted lineup
            continue

        if pos == 'gk':
            data = gk_data
        elif pos == 'd':
            data = d_data
        elif pos == 'm':
            data = m_data
        elif pos == 'st':
            data = st_data
        else:
            print(f'{player}: Position error')
            continue

        mins = x.find('td', attrs={'class': 'p0c-team-squad__cell-player p0c-team-squad__cell-player--time-played'}).text.strip()
        goals = x.find('td', attrs={'class': 'p0c-team-squad__cell-player p0c-team-squad__cell-player--goals'}).text.strip()
        assists = x.find('td', attrs={'class': 'p0c-team-squad__cell-player p0c-team-squad__cell-player--assists'}).text.strip()
        yellow = x.find('td', attrs={'class': 'p0c-team-squad__cell-player p0c-team-squad__cell-player--yellow-cards'}).text.strip()
        red = x.find('td', attrs={'class': 'p0c-team-squad__cell-player p0c-team-squad__cell-player--red-cards'}).text.strip()

        data[player] = []

        for i in (mins, goals, penaltyGoals, assists, yellow, red, sp, cp):
            if i == '-':
                data[player].append(0)
            else:
                data[player].append(int(i))

        playerCount += 1

# Print how many players are found to make sure that all 220 players are listed.
print()
print(f'{playerCount} players listed.')
