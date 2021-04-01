import pandas as pd
from scrape import scrape_main
import formulas
# formulas.py contains the mathematical models of the project. It is not on Github as my rivals could benefit from it.

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
    formulas.calculate_extra_columns(df)

# Calculate final points for players in each position
formulas.calculate_gk_points(gk_data)
formulas.calculate_d_points(d_data)
formulas.calculate_m_points(m_data)
formulas.calculate_st_points(st_data)

# FINALIZATION #################################
# Concatenate the m and st dataframes, and create another dataframe that contains all players
m_st_data = pd.concat((m_data, st_data))
all_data = pd.concat((gk_data, d_data, m_data, st_data))

html_renders = []

for df in (gk_data, d_data, m_st_data, all_data):
    # Sort by final_results
    df = df.sort_values(['pts_final'], ascending=False)

    # Add pg rows for analysis
    for col in ('Goals', 'PenaltyGoals', 'Assists', 'Yellow', 'Red'):
        if col == 'Goals':
            df[col + '_pg'] = (df[col] - df['PenaltyGoals']) / df['matches']
        else:
            df[col + '_pg'] = df[col] / df['matches']

    # Push final_results column to the back
    column_list = df.columns.tolist()
    temp = column_list.pop(8)
    column_list.append(temp)
    df = df[column_list]

    # Apply background_gradient and render html tables
    gradient_columns = ['Goals_pg', 'PenaltyGoals_pg', 'Assists_pg', 'Yellow_pg', 'Red_pg', 'SPrediction', 'CPrediction', 'pts_final']
    html_renders.append(df.style.background_gradient(subset=gradient_columns).render())

# Output to html file
with open('out.html', 'w', encoding='utf-8') as out:
    out.write("<head><meta charset='UTF-8'></head>")
    out.write("<h1>GOALKEEPERS</h1>")
    out.write(html_renders[0])
    out.write("<h1>DEFENDERS</h1>")
    out.write(html_renders[1])
    out.write("<h1>MIDFIELDERS & STRIKERS</h1>")
    out.write(html_renders[2])
    out.write("<h1>ALL PLAYERS</h1>")
    out.write(html_renders[3])
