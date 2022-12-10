import torch
from data import load_data, USED_NODE_ATTRIBUTES, scale_cheb_strength_score
from cheb_conv_model import ChebGNN
import pandas as pd
import warnings


model = ChebGNN(len(USED_NODE_ATTRIBUTES) + 5, 64)
model.load_state_dict(torch.load('cheb_conv.pt'))
model.eval()

def cheb_inference(data):
    data = load_data(data)
    return scale_cheb_strength_score(model(data.x, data.edge_index, data.edge_attr, data.batch).item())

def easy():
    data = pd.read_pickle("all_teams_players_pickle_position.pickle")
    real = data['real-madrid']
    print(cheb_inference(real))



def med_1():
    data = pd.read_pickle("all_teams_players_pickle_position.pickle")
    bayern = data['fc-bayern-munchen']
    barca = data['fc-barcelona']
    print('prior')
    print(cheb_inference(barca))
    barca.iloc[-1] = bayern.iloc[1]
    print('after')
    print(cheb_inference(barca))

def med_3():
    data = pd.read_pickle("all_teams_players_pickle_position.pickle")
    man = data['manchester-united']
    psg = data['fc-paris-saint-germain']
    print(cheb_inference(psg))

    psg.iloc[0] = man.iloc[1]
    print(cheb_inference(psg))

def med_2():
    data = pd.read_pickle("all_teams_players_pickle_position.pickle")
    mad = data['atletico-madrid']
    psg = data['fc-paris-saint-germain']

    print(cheb_inference(psg))

    psg.iloc[1] = mad.iloc[0]

    print(cheb_inference(psg))

def hard_case(): #lewandowski as striker
    data = pd.read_pickle("all_teams_players_pickle_position.pickle")
    bayern = data['fc-bayern-munchen']
    barca = data['fc-barcelona']

    print(cheb_inference(barca))

    barca.iloc[1] = bayern.iloc[1]
    print(cheb_inference(barca))


if __name__ == '__main__':
    with warnings.catch_warnings():
        med_2()