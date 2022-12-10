import torch
from torch.nn import Linear
import torch.nn.functional as F
from torch_geometric.nn import TAGConv, global_mean_pool

class TAGNN(torch.nn.Module):
    def __init__(self, num_node_features, hidden_channels):
        super().__init__()
        self.conv1 = TAGConv(num_node_features, hidden_channels, K=3)
        self.conv2 = TAGConv(hidden_channels, hidden_channels, K=3)
        self.conv3 = TAGConv(hidden_channels, hidden_channels, K=3)
        self.conv4 = TAGConv(hidden_channels, hidden_channels, K=3)
        self.conv5 = TAGConv(hidden_channels, hidden_channels, K=3)
        self.lin1 = Linear(hidden_channels, hidden_channels)
        self.lin2 = Linear(hidden_channels, 1)

    def forward(self, x, edge_index, edge_weight, batch, dropout=.1):
        x = self.conv1(x, edge_index, edge_weight)
        x = F.relu(x)
        x = self.conv2(x, edge_index, edge_weight)
        x = F.relu(x)
        x = self.conv3(x, edge_index, edge_weight)
        x = F.relu(x)
        x = self.conv4(x, edge_index, edge_weight)
        x = F.relu(x)
        x = self.conv5(x, edge_index, edge_weight)
        x = F.relu(x)
        x = global_mean_pool(x, batch)
        x = F.dropout(x, p=dropout)
        x = self.lin1(x)
        x = self.lin2(x)
        x = F.sigmoid(x)
        return x