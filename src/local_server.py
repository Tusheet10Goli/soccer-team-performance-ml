import mysql.connector
import pandas as pd
import pickle

# Database connection
conn = mysql.connector.connect(host='localhost', user='root', password='root', database='soccerdb')
cursor = conn.cursor()


def get_all_teams_players():
    team_list = get_all_teams_helper()
    team_dict = {}
    for team in team_list:
        team_dict[team] = get_playing_11_helper(team)
        print(f'{team} done.')
    return team_dict


def get_playing_11_helper(team_name):

    def get_best_player_by_position_club(position, count=1):
        query = f'Select * from players where current_club_id = {team_id} and position = "{position}" and last_season = 2021 order by cast(highest_market_value_in_gbp as unsigned int) desc limit {count}'
        return pd.read_sql(query, con=conn)

    query_team_id = f'select club_id from clubs where name = "{team_name}"'
    cursor.execute(query_team_id)
    team_id = cursor.fetchone()[0]
    # positions = ['Centre-Forward', 'Left Winger', 'Right Winger', ('Central Midfield', 3), 'Right-Back', 'Left-Back', ('Centre-Back', 2), 'Goalkeeper']
    positions = [('Attack', 3), ('Midfield', 3),
                 ('Defender', 4), 'Goalkeeper']
    players = pd.DataFrame()

    for position in positions:
        if type(position) is tuple:
            players = pd.concat([players, get_best_player_by_position_club(position[0], position[1])])
        else:
            players = pd.concat([players, get_best_player_by_position_club(position)])

    return players


def get_all_teams_helper():
    query = 'SELECT name FROM clubs ORDER BY name ASC;'
    cursor.execute(query)
    res = cursor.fetchall()
    team_list = []
    for i in res:
        team_list.append(i[0])
    return team_list
def get_edge_weight_helper(player_1_id, player_2_id):
    score = 0
    player_1_q = f"Select * from players where player_id = {player_1_id}"
    player_2_q = f'select * from players where player_id = {player_2_id}'

    player_1 = pd.read_sql(player_1_q, con=conn).to_dict('records')[0]
    player_2 = pd.read_sql(player_2_q, con=conn).to_dict('records')[0]

    if player_1['current_club_id'] == player_2['current_club_id']:
        score += 0.5

    if player_1['country_of_birth'] == player_2['country_of_birth']:
        score += 0.1

    if player_1['country_of_citizenship'] == player_2['country_of_citizenship']:
        score += 0.25

    player_club_1 = pd.read_sql(f'select * from clubs where club_id = {player_1["current_club_id"]}', con=conn).to_dict('records')[0]
    player_club_2 = pd.read_sql(f'select * from clubs where club_id = {player_2["current_club_id"]}', con=conn).to_dict('records')[0]

    if player_club_1['domestic_competition_id'] == player_club_2['domestic_competition_id']:
        score += 0.15

    matches_together = f'select a.game_id, a.player_id as player_1_id, b.player_id as player_2_id, a.player_club_id as player_1_club, b.player_club_id as player_2_club ' \
                           f'from appearances as a join appearances as b on a.game_id = b.game_id and a.player_club_id = b.player_club_id where a.player_id = {player_1_id} and b.player_id = {player_2_id}'
    matches_against = f'select a.game_id, a.player_id as player_1_id, b.player_id as player_2_id, a.player_club_id as player_1_club, b.player_club_id as player_2_club ' \
                           f'from appearances as a join appearances as b on a.game_id = b.game_id and a.player_club_id != b.player_club_id where a.player_id = {player_1_id} and b.player_id = {player_2_id}'
    cursor.execute(matches_together)
    num_games_together = len(cursor.fetchall())
    cursor.execute(matches_against)
    num_games_against = len(cursor.fetchall())

    total_num_games = num_games_against + num_games_together

    if total_num_games == 0:
        return score

    match_score = (0.8 * num_games_together/total_num_games) + (0.2 * num_games_against/total_num_games)
    total_score = score * 0.8 + match_score * 0.2
    return total_score

if __name__ == '__main__':
    with open("all_teams_players_pickle_position.pickle", 'wb') as f:
        pickle.dump(get_all_teams_players(), f)

    with open("all_teams_players_pickle_position.pickle", 'rb') as f:
        dic = pickle.load(f)
