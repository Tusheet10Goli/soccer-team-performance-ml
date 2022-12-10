import mysql.connector
import pandas as pd

conn = mysql.connector.connect(host='localhost', user='root', password='root', database='soccerdb')
cursor = conn.cursor()

df = pd.read_sql('SELECT home_club_id, away_club_id, home_club_goals, away_club_goals  FROM games', conn)
new_df = pd.DataFrame(columns=['club_id', 'result'])

for idx, row in df.iterrows():
    if row['home_club_goals'] > row['away_club_goals']:
        new_df = pd.concat([new_df, pd.DataFrame({
            'club_id': [row['home_club_id'], row['away_club_id']],
            'result': [1, 0]
        })], ignore_index=True)
    elif row['home_club_goals'] < row['away_club_goals']:
        new_df = pd.concat([new_df, pd.DataFrame({
            'club_id': [row['home_club_id'], row['away_club_id']],
            'result': [0, 1]
        })], ignore_index=True)
    else:
        new_df = pd.concat([new_df, pd.DataFrame({
            'club_id': [row['home_club_id'], row['away_club_id']],
            'result': [0.5, 0.5]
        })], ignore_index=True)

df = new_df.groupby(['club_id'], as_index=False).mean()
df['club_id'] = df['club_id'].astype(int)
new_df = pd.read_sql('SELECT club_id, name FROM clubs', conn)
df = pd.merge(df, new_df, on='club_id')
df.to_csv('./label.csv')
