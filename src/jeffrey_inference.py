import pandas as pd
from jeffrey_model import *
from data import load_data, USED_NODE_ATTRIBUTES
import warnings

model = TAGNN(len(USED_NODE_ATTRIBUTES) + 5, 64)
model.load_state_dict(torch.load('saved_weights_test.pt'))
model.eval()

def inference(data):
    data = load_data(data)
    model.eval()
    return model(data.x, data.edge_index, data.edge_attr, data.batch).item()*100

def easy():
    data = pd.read_pickle('all_teams_players_pickle_position.pickle')
    print('Easy Test:\nReal Madrid -', inference(data['real-madrid']))
    print()

def med_1():
    data = pd.read_pickle('all_teams_players_pickle_position.pickle')
    barcelona = data['fc-barcelona']
    bayern = data['fc-bayern-munchen']
    # print(bayern.iloc[1])
    print('Medium Test 1:')
    print('Barcelona -', inference(barcelona))
    barcelona.iloc[-1] = bayern.iloc[1]
    print('Barcelona with Lewandowski as goalkeeper -', inference(barcelona))
    print()
    
def med_2():
    data = pd.read_pickle('all_teams_players_pickle_position.pickle')
    psg = data['fc-paris-saint-germain']
    manu = data['manchester-united']
    print('Medium Test 2:')
    print('PSG -', inference(psg))
    psg.iloc[0] = manu.iloc[1]
    print('PSG with Messi -', inference(psg))
    print()

def med_3():
    data = pd.read_pickle('all_teams_players_pickle_position.pickle')
    psg = data['fc-paris-saint-germain']
    mad = data['atletico-madrid']
    print('Medium Test 3:')
    print('PSG -', inference(psg))
    psg.iloc[1] = mad.iloc[0]
    print('PSG with Ronaldo -', inference(psg))
    print()

def hard():
    data = pd.read_pickle('all_teams_players_pickle_position.pickle')
    barcelona = data['fc-barcelona']
    bayern = data['fc-bayern-munchen']
    print('Hard Test:')
    print('Barcelona -', inference(barcelona))
    barcelona.iloc[1] = bayern.iloc[1]
    print('Barcelona with Lewandowski as striker -', inference(barcelona))
    print()

def test():
    data = pd.read_pickle('all_teams_players_pickle_position.pickle')
    print('Test:')
    print('Barcelona - ', inference(data['fc-barcelona']))
    print()

warnings.filterwarnings('ignore')

# test()
# easy()
# med_1()
# med_2()
# med_3()
# hard()
