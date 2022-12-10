import pandas as pd
from jeffrey_model import *
from data import load_data, USED_NODE_ATTRIBUTES
import warnings
warnings.filterwarnings('ignore')

model = TAGNN(len(USED_NODE_ATTRIBUTES) + 5, 64)
model.load_state_dict(torch.load('saved_weights_tag.pt'))
model.eval()

def inference(data):
    # print(data)
    data = load_data(data)
    model.eval()
    return model(data.x, data.edge_index, data.edge_attr, data.batch).item()*100

def win(team_a, team_b):
    a_score = inference(team_a)
    b_score = inference(team_b)
    return a_score > b_score

def accuracy(game_data):
    data = pd.read_pickle('all_teams_players_pickle_position.pickle')
    count = 0
    accurate = 0
    # print(data[0])
    for team_a,games in game_data.items():
        team_a = data[team_a.replace(' ', '-').lower()]
        if len(team_a)<11:
            continue
        for team_b, score in games:
            team_b = data[team_b.replace(' ', '-').lower()]
            if len(team_b)<11 or score == 0:
                continue
            
            if score > 0:
                accurate += win(team_a,team_b)
            else:
                # print(win(data['ud-almeria'],data['fc-barcelona']))
                accurate += win(team_b,team_a)
            count += 1
            print(accurate/count)
        
        # if score != 0:
            # print(team_b)
            # print(len(data[team_a]),len(data[team_b]))
            # if score != 0 and len(data[team_a])>10 and len(data[team_b])>10:
                # print(team_a, 'DAB')
                # print(data[team_a.replace(' ', '-').lower()])
                # print(team_b, 'DAB')
                # print(data[team_b.replace(' ', '-').lower()])
                # if score > 0:
                #     accurate += win(data[team_a],data[team_b])
                # else:
                #     # print(win(data['ud-almeria'],data['fc-barcelona']))
                #     accurate += win(data[team_b],data[team_a])
                # count += 1
    accuracy = accurate/count
    return accuracy

data = pd.read_pickle('game_dict.pickle')
print(accuracy(data))



