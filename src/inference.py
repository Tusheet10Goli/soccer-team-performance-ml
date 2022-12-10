import torch
from torch_geometric.loader import DataLoader
from data import load_data, USED_NODE_ATTRIBUTES
from model import GNN

model = GNN(len(USED_NODE_ATTRIBUTES) + 5, 64)
model.load_state_dict(torch.load('saved_weights.pt'))
model.eval()

# Assuming data is a pandas dataframe consisting of players
# Using predefined atttributes
def inference(data):
    data = load_data(data)
    return model(data.x, data.edge_index, data.edge_attr, data.batch).item()


if __name__ == '__main__':
    import pandas as pd
    data = pd.read_pickle("all_teams_players_pickle_position.pickle")
    barca_data = data['fc-barcelona']
    print(inference(barca_data))
