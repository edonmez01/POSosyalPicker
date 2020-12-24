import pandas as pd
import math
from scrape import scrape_main

# Set parameters for console display
pd.set_option('display.max_columns', 25)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 1000)

# Initialize dataframes
data_cols = ['Mins', 'Goals', 'PenaltyGoals', 'Assists', 'Yellow', 'Red', 'SPrediction', 'CPrediction']
gk_data = pd.DataFrame.from_dict(scrape_main.gk_data, orient='index', columns=data_cols)
d_data = pd.DataFrame.from_dict(scrape_main.d_data, orient='index', columns=data_cols)
m_data = pd.DataFrame.from_dict(scrape_main.m_data, orient='index', columns=data_cols)
st_data = pd.DataFrame.from_dict(scrape_main.st_data, orient='index', columns=data_cols)

# Calculate extra columns
for df in (gk_data, d_data, m_data, st_data):
    df['pts_final'] = 0
    df['matches'] = df['Mins'] / 90
    df['clean_sheet_prob'] = 1 / (df['CPrediction'] + 1)
    df['goal_multiplier'] = [math.log(i + 1.1, 2.5) for i in df['SPrediction']]
    df['win_prob'] = [2 / (1 + math.exp(c - s)) - 1 for c, s in zip(df['CPrediction'], df['SPrediction'])]
    df['pts_final'] -= df['Yellow'] / df['matches']
    df['pts_final'] -= 4 * (df['Red'] / df['matches'])
    df['pts_final'] += df['win_prob']

# GK #######################################
# 10 pts per goal
gk_data['pts_final'] += 10 * (((gk_data['Goals'] - gk_data['PenaltyGoals']) / gk_data['matches']) * gk_data['goal_multiplier'] + 1.3 * gk_data['PenaltyGoals'] / gk_data['matches'])

# 8 pts per assist
gk_data['pts_final'] += 8 * (gk_data['Assists'] / gk_data['matches']) * gk_data['goal_multiplier']

# -1 point per goal conceded
gk_data['pts_final'] -= gk_data['CPrediction']

# 5 pts for clean sheet
gk_data['pts_final'] += 5 * gk_data['clean_sheet_prob']


# D #########################################
# 8 pts per goal
d_data['pts_final'] += 8 * (((d_data['Goals'] - d_data['PenaltyGoals']) / d_data['matches']) * d_data['goal_multiplier'] + 1.3 * d_data['PenaltyGoals'] / d_data['matches'])

# 4 pts per assist
d_data['pts_final'] += 4 * (d_data['Assists'] / d_data['matches']) * d_data['goal_multiplier']

# -0.5 pts per goal conceded
d_data['pts_final'] -= d_data['CPrediction'] / 2

# 3 pts for clean sheet
d_data['pts_final'] += 3 * d_data['clean_sheet_prob']


# M #########################################
# 6 pts per goal
m_data['pts_final'] += 6 * (((m_data['Goals'] - m_data['PenaltyGoals']) / m_data['matches']) * m_data['goal_multiplier'] + 1.3 * m_data['PenaltyGoals'] / m_data['matches'])

# 3 pts per assist
m_data['pts_final'] += 3 * (m_data['Assists'] / m_data['matches']) * m_data['goal_multiplier']


# ST ##########################################
# 5 pts per goal
st_data['pts_final'] += 5 * (((st_data['Goals'] - st_data['PenaltyGoals']) / st_data['matches']) * st_data['goal_multiplier'] + 1.3 * st_data['PenaltyGoals'] / st_data['matches'])

# 3 pts per assist
st_data['pts_final'] += 3 * (st_data['Assists'] / st_data['matches']) * st_data['goal_multiplier']


# FINALIZATION #################################
# Concatenate the dataframes
final_results = pd.concat((gk_data, d_data, m_data, st_data))

# Sort by final_results
final_results = final_results.sort_values(['pts_final'], ascending=False)

# Add pg rows for analysis
for col in ('Goals', 'PenaltyGoals', 'Assists', 'Yellow', 'Red'):
    if col == 'Goals':
        final_results[col + '_pg'] = (final_results[col] - final_results['PenaltyGoals']) / final_results['matches']
    else:
        final_results[col + '_pg'] = final_results[col] / final_results['matches']

# Push final_results column to the back
column_list = final_results.columns.tolist()
temp = column_list.pop(8)
column_list.append(temp)
final_results = final_results[column_list]

# Apply background_gradient and render html table
gradient_columns = ['Goals_pg', 'PenaltyGoals_pg', 'Assists_pg', 'Yellow_pg', 'Red_pg', 'SPrediction', 'CPrediction', 'pts_final']
html_render = final_results.style.background_gradient(subset=gradient_columns).render()

# Output to html file
with open('out.html', 'w', encoding='utf-8') as out:
    out.write("<head><meta charset='UTF-8'></head>")
    out.write(html_render)
