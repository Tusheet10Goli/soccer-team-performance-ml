from flask import Flask
from flask import jsonify
import mysql.connector
import pickle
import pandas as pd
from flask_cors import CORS
from inference import inference
from helper import *
from cheb_conv_inference import *
import aman_api as a_api
import jeffrey_inference as jf
import atexit

app = Flask(__name__)
CORS(app)

# Python Flask Info: https://towardsdatascience.com/creating-restful-apis-using-flask-and-python-655bad51b24

# API Endpoints
# Check if server is up and running
@app.route('/health-check', methods=['GET'])
def health_check():
    return jsonify({'name': 'health-check', 'status': 'ACTIVE'})


# Get starting 11 for one team
@app.route('/get-one-team-players/<team_name>', methods=['GET'])
def get_one_team_players(team_name):
    global current_team
    current_team = get_playing_11_helper(team_name)
    players_dict = current_team.to_dict('records')
    return jsonify({'name': 'get-one-team-players', 'status': 'ACTIVE', 'players': players_dict})


# Get list of all teams
@app.route('/get-all-teams', methods=['GET'])
def get_all_teams():
    team_list = get_all_teams_helper()
    return jsonify({'name': 'get-all-teams', 'status': 'ACTIVE', 'number_of_teams': len(team_list), 'teams': team_list})


# Get list of all players
@app.route('/get-all-players', methods=['GET'])
def get_all_players():
    conn, cursor = create_conn()
    query = 'SELECT pretty_name FROM players ORDER BY pretty_name ASC;'
    cursor.execute(query)
    res = cursor.fetchall()
    close_conn(conn, cursor)
    player_list = []
    for i in res:
        player_list.append(i[0])
    return jsonify({'name': 'get-all-players', 'status': 'ACTIVE', 'number_of_players': len(player_list), 'players': player_list})


# Get list of all competitions
@app.route('/get-all-competitions', methods=['GET'])
def get_all_competitions():
    conn, cursor = create_conn()
    query = 'SELECT name FROM competitions ORDER BY name ASC;'
    cursor.execute(query)
    res = cursor.fetchall()
    close_conn(conn, cursor)
    competition_list = []
    for i in res:
        competition_list.append(i[0])
    return jsonify({'name': 'get-all-competitions', 'status': 'ACTIVE', 'number_of_competitions': len(competition_list), 'players': competition_list})


# Get list of all players from a specific club
@app.route('/get-all-players_from_club/<club_name>', methods=['GET'])
def get_all_players_from_club(club_name):
    # get club_id
    conn, cursor = create_conn()
    q = 'SELECT club_id FROM clubs WHERE name=%s OR pretty_name=%s;'
    cursor.execute(q, [str(club_name), str(club_name)])
    r = cursor.fetchall()
    if (len(r) == 0):
        return jsonify({'name': 'get-all-players-from-club', 'status': 'ERROR', 'message': 'INVALID CLUB NAME'})
    club_id = r[0][0]

    # get all players based on club id
    query = 'SELECT pretty_name FROM players WHERE current_club_id=%s ORDER BY pretty_name ASC;'
    cursor.execute(query, [str(club_id)])
    res = cursor.fetchall()
    close_conn(conn, cursor)
    player_list = []
    for i in res:
        player_list.append(i[0])
    return jsonify({'name': 'get-all-players-from-club', 'status': 'ACTIVE', 'number_of_players': len(player_list), 'players': player_list})


# Search for a player (dropdown filter)
@app.route('/search-player/<player_name>/<club_name>/<nationality>/<position>', methods=['GET'])
def search_player(player_name, club_name, nationality, position):
    conn, cursor = create_conn()
    # filter variables
    if player_name == '*': player_name = ''
    if club_name == '*': club_name = ''
    if nationality == '*': nationality = ''
    if position == '*': position = ''

    # default (all players)
    if player_name == '' and club_name == '' and nationality == '' and position == '':
        player_list = []
        query = 'SELECT pretty_name FROM players ORDER BY pretty_name ASC;'
        cursor.execute(query)
        res = cursor.fetchall()
        for i in res:
            player_list.append(i[0])
        return jsonify({'name': 'search-player', 'status': 'ACTIVE', 'number_of_players': len(player_list), 'players': player_list})

    # get club_id
    q = 'SELECT club_id FROM clubs WHERE name LIKE %s OR pretty_name LIKE %s;'
    cursor.execute(q, ['%' + str(club_name) + '%', '%' + str(club_name) + '%'])
    r = cursor.fetchall()
    if (len(r) == 0):
        return jsonify({'name': 'search-player', 'status': 'ERROR', 'message': 'INVALID CLUB NAME'})

    player_list = []
    # get all players based on club id
    for club_id in r:
        club_id = club_id[0]
        query = 'SELECT * FROM players WHERE current_club_id=%s AND (name LIKE %s OR pretty_name LIKE %s) AND country_of_citizenship LIKE %s AND position LIKE %s ORDER BY pretty_name ASC;'
        cursor.execute(query, [str(club_id), '%' + str(player_name) + '%', '%' + str(player_name) + '%', '%' + str(nationality) + '%', '%' + str(position) + '%'])
        res = cursor.fetchall()
        for i in res:
            player_list.append(i[0])
    close_conn(conn, cursor)
    return jsonify({'name': 'search-player', 'status': 'ACTIVE', 'number_of_players': len(player_list), 'players': player_list})


# TODO: Recalculate score with custom team (takes in a list of dfs)
@app.route('/calculate-score', methods=['GET'])
def calculate_score():
    global aman_player_dict
    score = {'GraphConv': round(inference(current_team) * 100.0, 3),
             'ChebyShev': round(cheb_inference(current_team), 3),
             'TAGConv': round(jf.inference(current_team), 3)
            }
    player_list = []
    c = 0
    for p in current_team.name.tolist():
        modified_p = p.replace('-', '').lower()
        if modified_p in aman_player_dict:
            player_list.append(aman_player_dict[modified_p])
        else:
            score['CustomNN'] = 'N/A'
            break
    if len(player_list) >= 9:
        aman_input = aman_players[aman_players['Player'].isin(player_list)]
        score['CustomNN'] = round(a_api.inference(aman_input), 3)
    return jsonify({'name': 'calculate-score', 'status': 'ACTIVE', 'score': score})

# @app.route('/update-model/{model}', methods=['POST'])
# def update_model(model):
#     global curr_model
#     curr_model = model
#     return jsonify({'name': 'update-model', 'status': 'ACTIVE', 'current_model': curr_model})



@app.route('/replace-player/<old_player_id>/<new_player_id>', methods=['POST'])
def replace_player(old_player_id, new_player_id):
    conn, cursor = create_conn()
    global current_team
    current_team = current_team[current_team.player_id != int(old_player_id)]
    query = f'SELECT * FROM players WHERE player_id={new_player_id}'
    player_df = pd.read_sql(query, con=conn)
    current_team = pd.concat([current_team, player_df])
    close_conn(conn, cursor)
    return jsonify({'name': 'replace-player', 'status': 'ACTIVE'})


# Edge weight call for front end (API)
@app.route('/get-edge-weight/<player_1_id>/<player_2_id>', methods=['GET'])
def get_edge_weight(player_1_id, player_2_id):
    edge_weight = get_edge_weight_helper(player_1_id, player_2_id)
    return jsonify({'name': 'get-edge-weight', 'status': 'ACTIVE', 'edge_weight': edge_weight})


def onAppClose():
    onexit()


if __name__ == '__main__':
    with open("all_teams_players_pickle_position.pickle", 'rb') as f:
        team_dic = pickle.load(f)
    curr_model = 'OLD'
    aman_players = pd.read_csv('all-players')
    aman_player_dict = get_unicode_dict(aman_players.Player.tolist())
    current_team = get_playing_11_helper('manchester-city')
    atexit.register(onAppClose)
    app.run(host='0.0.0.0', port=105)
