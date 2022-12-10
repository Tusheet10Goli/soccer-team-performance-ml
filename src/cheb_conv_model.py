import torch
from torch.nn import Linear
import torch.nn.functional as F
from torch_geometric.nn import ChebConv
from torch_geometric.nn import global_mean_pool, global_max_pool, global_sort_pool


class ChebGNN(torch.nn.Module):

    def __init__(self, num_node_features, hidden_channels):
        super().__init__()
        self.conv1 = ChebConv(num_node_features, hidden_channels, K=5)
        self.conv2 = ChebConv(hidden_channels, hidden_channels, K=5)
        self.conv3 = ChebConv(hidden_channels, hidden_channels, K=5)
        self.linear_1 = Linear(hidden_channels, hidden_channels)
        self.linear = Linear(hidden_channels, 1)


    def forward(self, x, edge_index, edge_weight, batch):
        x = self.conv1(x, edge_index, edge_weight=edge_weight)
        x = x.relu()
        x = F.dropout(x, p=0.5, training=self.training)

        x = self.conv2(x, edge_index, edge_weight=edge_weight)
        x = F.dropout(x, p=0.5, training=self.training)

        x = self.conv3(x, edge_index, edge_weight=edge_weight)
        x = x.relu()
        x = global_mean_pool(x, batch)
        x = F.dropout(x, p=0.5, training=self.training)
        x = x.relu()
        x = self.linear_1(x)
        x = self.linear(x)
        x = F.sigmoid(x)
        return x