import mysql.connector
import pickle
import pandas as pd
from unidecode import unidecode
from collections import defaultdict
# Get starting 11 for all teams
def get_all_teams_players():
    with open("all_teams_players_pickle.pickle", 'rb') as f:
        team_dic = pickle.load(f)
    return team_dic

def get_all_team_games():
    with open("game_dict.pickle", 'rb') as f:
        game_dic = pickle.load(f)
    return game_dic


def get_playing_11_helper(team_name):
    if team_name in team_dic:
        return team_dic[team_name]
    else:
        def get_best_player_by_position_club(team_id, position, count=1):
            conn, cursor = create_conn()
            query = f'Select * from players where current_club_id = {team_id} and position = "{position}" and last_season = 2021 order by cast(highest_market_value_in_gbp as unsigned int) desc limit {count}'
            res = pd.read_sql(query, con=conn)
            close_conn(conn, cursor)
            return res

        conn, cursor = create_conn()
        query_team_id = f'SELECT club_id FROM clubs WHERE name="{team_name}" OR pretty_name="{team_name}"'
        cursor.execute(query_team_id)
        team_id = cursor.fetchone()[0]
        close_conn(conn, cursor)
        positions = [('Attack', 3), ('Midfield', 3),
                     ('Defender', 4), 'Goalkeeper']
        players = pd.DataFrame()
        for position in positions:
            if type(position) is tuple:
                players = pd.concat(
                    [players, get_best_player_by_position_club(team_id, position[0], position[1])])
            else:
                players = pd.concat(
                    [players, get_best_player_by_position_club(team_id, position)])
        return players

def get_playing_11_helper_prem(team_name):
    pass

def store_all_team_game_data():
    conn, cursor = create_conn()
    query = 'select t.pretty_name as home, t1.pretty_name as away, (g.home_club_goals-g.away_club_goals) ' \
            'as gd from games as g join clubs t on ' \
            'g.home_club_id = t.club_id join clubs as t1 on g.away_club_id = t1.club_id;'
    cursor.execute(query)
    res = cursor.fetchall()
    close_conn(conn, cursor)
    dic = defaultdict(lambda: list())
    for g in res:
        dic[g[0]].append((g[1], g[2]))
        dic[g[1]].append((g[0], -1*g[2]))
    with open('game_dict.pickle', 'wb') as f:
        pickle.dump(dict(dic), f)
    return dic

def get_all_teams_helper():
    conn, cursor = create_conn()
    query = 'SELECT pretty_name FROM clubs ORDER BY pretty_name ASC;'
    cursor.execute(query)
    res = cursor.fetchall()
    close_conn(conn, cursor)
    team_list = []
    for i in res:
        if len(team_dic[i[0]]) != 0:
            team_list.append(i[0])
    return team_list


# Edge weight call for backend
def get_edge_weight_helper(player_1_id, player_2_id):
    player_1_id = int(player_1_id)
    player_2_id = int(player_2_id)

    if (player_1_id, player_2_id) in edge_dict:
        return edge_dict[(player_1_id, player_2_id)]
    if (player_2_id, player_1_id) in edge_dict:
        return edge_dict[(player_2_id, player_1_id)]

    score = 0
    conn, cursor = create_conn()
    player_1_q = f"SELECT * FROM players WHERE player_id={player_1_id}"
    player_2_q = f'SELECT * FROM players WHERE player_id={player_2_id}'

    player_1 = pd.read_sql(player_1_q, con=conn).to_dict('records')[0]
    player_2 = pd.read_sql(player_2_q, con=conn).to_dict('records')[0]
    close_conn(conn, cursor)

    if player_1['current_club_id'] == player_2['current_club_id']:
        score += 0.5
    if player_1['country_of_birth'] == player_2['country_of_birth']:
        score += 0.1
    if player_1['country_of_citizenship'] == player_2['country_of_citizenship']:
        score += 0.25
    
    conn, cursor = create_conn()
    player_club_1 = pd.read_sql(f'SELECT * FROM clubs WHERE club_id={player_1["current_club_id"]}', con=conn).to_dict('records')[0]
    player_club_2 = pd.read_sql(f'SELECT * FROM clubs WHERE club_id={player_2["current_club_id"]}', con=conn).to_dict('records')[0]
    close_conn(conn, cursor)

    if player_club_1['domestic_competition_id'] == player_club_2['domestic_competition_id']:
        score += 0.15

    matches_together = f'SELECT a.game_id, a.player_id AS player_1_id, b.player_id AS player_2_id, a.player_club_id AS player_1_club, b.player_club_id AS player_2_club ' \
                           f'FROM appearances AS a JOIN appearances AS b ON a.game_id=b.game_id AND a.player_club_id=b.player_club_id WHERE a.player_id={player_1_id} AND b.player_id={player_2_id}'
    matches_against = f'SELECT a.game_id, a.player_id AS player_1_id, b.player_id AS player_2_id, a.player_club_id AS player_1_club, b.player_club_id AS player_2_club ' \
                           f'FROM appearances AS a JOIN appearances AS b ON a.game_id=b.game_id AND a.player_club_id!=b.player_club_id WHERE a.player_id={player_1_id} AND b.player_id={player_2_id}'
    
    conn, cursor = create_conn()
    cursor.execute(matches_together)
    num_games_together = len(cursor.fetchall())
    cursor.execute(matches_against)
    num_games_against = len(cursor.fetchall())
    close_conn(conn, cursor)
    total_num_games = num_games_against + num_games_together
    if total_num_games == 0:
        return score
    match_score = (0.8 * num_games_together/total_num_games) + (0.2 * num_games_against/total_num_games)
    total_score = score * 0.8 + match_score * 0.2
    edge_dict[(player_1_id, player_2_id)] = total_score

    with open('edge_dict.pickle', 'wb') as f:
        pickle.dump(edge_dict, f)

    return total_score

def get_unicode_dict(names):
    ans = dict()
    for n in names:
        ans[unidecode(n).replace(' ', '').lower()] = n
    return ans

def create_conn():
    # Database connection
    conn = mysql.connector.connect(host='us-cdbr-east-05.cleardb.net', user='b9b54aeb98bf69', password='f240f4a7', database='heroku_db48141a90d46f7')
    cursor = conn.cursor()

    # Local database connection
    # conn = mysql.connector.connect(host='localhost', user='root', password='root', database='soccerdb')
    # cursor = conn.cursor()
    return conn, cursor


def close_conn(conn, cursor):
    cursor.close()
    conn.close()


def onexit():
    print('on exit called')


with open("all_teams_players_pickle_position.pickle", 'rb') as f:
    team_dic = pickle.load(f)
with open("edge_dict.pickle", 'rb') as f:
    edge_dict = pickle.load(f)

if __name__ == '__main__':
    get_all_team_games()
