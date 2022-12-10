import pandas as pd
import torch
import numpy as np
from torch_geometric.data import Data
from helper import get_edge_weight_helper


USED_NODE_ATTRIBUTES = ["date_of_birth", "position", "foot", "height_in_cm", "market_value_in_gbp"]


def load_labels():
    results = pd.read_csv("label.csv")
    results.fillna(0)
    results_dict = {}
    for index, row in results.iterrows():
        results_dict[row['name']] = row['result']
    return results_dict


def preprocess_data(club_team):
    club_team = club_team[USED_NODE_ATTRIBUTES]
    club_team = club_team.dropna()

    # Grab Year
    club_team['date_of_birth'] = pd.to_datetime(club_team['date_of_birth'])
    club_team['year'] = pd.DatetimeIndex(club_team['date_of_birth']).year
    club_team = club_team.drop('date_of_birth', axis=1)

    # Position One-Hot
    positions = pd.get_dummies(club_team['position'], columns=['Attack', 'Defender', 'Goalkeeper', 'Midfield'])
    club_team = pd.concat([club_team, positions], axis=1)
    club_team = club_team.drop('position', axis=1)

    for pos in ['Attack', 'Defender', 'Goalkeeper', 'Midfield']:
        if pos not in club_team.columns:
            club_team[pos] = 0

    # Foot One-hot
    foot = pd.get_dummies(club_team['foot'], columns=['Both', 'Left', 'Right'])
    if '' in foot.columns:
        foot = foot.drop('', axis=1)
    foot = foot.loc[:, ~foot.columns.str.contains('^Unnamed')]
    club_team = pd.concat([club_team, foot], axis=1)
    club_team = club_team.drop('foot', axis=1)

    for f in ['Both', 'Left', 'Right']:
        if f not in club_team.columns:
            club_team[f] = 0

    club_team = club_team.apply(pd.to_numeric, errors='coerce')
    club_team = club_team.dropna()

    # Height Normalization
    club_team['height_in_cm'] = club_team['height_in_cm'] / 200.0

    # Market Value Normalization
    club_team['market_value_in_gbp'] = club_team['market_value_in_gbp'] / 2e7

    # Year Normalization
    club_team['year'] = (club_team['year'] - 1950) / 100

    club_team = club_team.to_numpy()

    # Normalization doesn't work because not on whole dataset
    # Manual normalization

    # from sklearn.preprocessing import normalize
    # if len(club_team) > 0:
    #     club_team = normalize(club_team, axis=0, norm='max')
    return club_team

# Assuming data is a pandas dataframe consisting of players
# Using attributes from USED_NODE_ATTRIBUTES defined above
def load_data(data):
    nodes = preprocess_data(data)
    if len(nodes) == 0:
        return
    x = torch.tensor(nodes).float()
    edge_a = []
    edge_b = []
    edge_attr = list()
    for i in range(len(x)):
        for j in range(len(x)):
            if i == j:
                continue
            edge_a.append(i)
            edge_b.append(j)
            edge_attr.append( get_edge_weight_helper (data.iloc[i]['player_id'], data.iloc[j]['player_id']))
    edge_index = torch.tensor([edge_a, edge_b]).long()
    edge_attr = torch.tensor(edge_attr).unsqueeze(-1)
    data_c = Data(x=x,edge_index=edge_index, edge_attr=edge_attr)
    return data_c

def scale_cheb_strength_score(score, feat_tot=len(USED_NODE_ATTRIBUTES)):
    return (score / (1 + feat_tot / 100))*100


def load_local_data():
    data = pd.read_pickle("all_teams_players_pickle_position.pickle")
    dataset = []
    metadata = {'num_node_features': len(USED_NODE_ATTRIBUTES) + 5}
    for club_team_name in data:
        club_team = data[club_team_name]
        nodes = preprocess_data(club_team)
        if len(nodes) == 0:
            continue
        team_dict = load_labels()
        x = torch.tensor(nodes).float()
        y = torch.tensor([team_dict[club_team_name]]).float()
        edge_a = []
        edge_b = []
        edge_attr = list()
        for i in range(len(x)):
            for j in range(len(x)):
                if i == j:
                    continue
                edge_a.append(i)
                edge_b.append(j)
                edge_attr.append( get_edge_weight_helper (club_team.iloc[i]['player_id'], club_team.iloc[j]['player_id']))
        edge_index = torch.tensor([edge_a, edge_b]).long()
        edge_attr = torch.tensor(edge_attr).unsqueeze(-1)
        data_c = Data(x=x, y=y, edge_index=edge_index, edge_attr=edge_attr)
        dataset.append(data_c)
    return dataset, metadata
