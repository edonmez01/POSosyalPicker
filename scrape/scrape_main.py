import requests
from bs4 import BeautifulSoup
from scrape import database
# scrape/database.py includes a list of predicted lineups, updated every week. It is not on Github as it could benefit my rivals.

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

# This variable is either ' KARAGUMRUK' or ' KASIMPASA'. We need it to check which one of the Yusuf Erdogans in the
# league we are dealing with.
yusuferdogan = ' KARAGUMRUK'

for team in teams.items():
    teamCount = 0
    link = team[0]
    sp, cp = team[1]
    r = requests.get(link)
    source = BeautifulSoup(r.content, 'html.parser').find_all('tr', attrs={'class': 'p0c-team-squad__row'})

    if sp is None and cp is None:  # If the team is not playing this week
        continue

    for x in source:
        player = x.find('a', attrs={'class': 'p0c-team-squad__player-name'}).text.strip()

        # Because there are 2 different Yusuf Erdogans in the league, the name of the player's team is appended to the
        # string.
        if player == 'Yusuf Erdoğan':
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

        # Some youth players seem to exist on the Mackolik source code but not in the real site. This is not a big deal
        # as these players don't play in the league anyway.
        try:
            temp = positions[player]
            if isinstance(temp, str):
                pos = positions[player]
                penaltyGoals = '-'
            else:
                pos, penaltyGoals = positions[player]

        except KeyError:
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

        apps = x.find('td', attrs={'class': 'p0c-team-squad__cell-player p0c-team-squad__cell-player--appearances'}).text.strip()
        mins = x.find('td', attrs={'class': 'p0c-team-squad__cell-player p0c-team-squad__cell-player--time-played'}).text.strip()
        goals = x.find('td', attrs={'class': 'p0c-team-squad__cell-player p0c-team-squad__cell-player--goals'}).text.strip()
        assists = x.find('td', attrs={'class': 'p0c-team-squad__cell-player p0c-team-squad__cell-player--assists'}).text.strip()
        yellow = x.find('td', attrs={'class': 'p0c-team-squad__cell-player p0c-team-squad__cell-player--yellow-cards'}).text.strip()
        red = x.find('td', attrs={'class': 'p0c-team-squad__cell-player p0c-team-squad__cell-player--red-cards'}).text.strip()

        # Mackolik is inconsistent with the stats of players that are transferred from one Super Lig team to another,
        # and therefore sometimes situations occur where a player has more penalty goals than total goals (because
        # total goals are reset to zero whereas penalty goals aren't).
        if penaltyGoals != '-' and penaltyGoals > int(goals):
            print(f'{player}: Penalty stats error')

        data[player] = []

        for i in (apps, mins, goals, penaltyGoals, assists, yellow, red, sp, cp):
            if i == '-':
                data[player].append(0)
            else:
                data[player].append(int(i))

        playerCount += 1
        teamCount += 1

    if teamCount != 11:
        print(f'Warning: {teamCount} players in {link}')

# Print how many players are found to make sure that all 220 players are listed.
print()
print(f'{playerCount} players listed.')
# print(check)
