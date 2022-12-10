import torch
from torch.nn import Linear
import torch.nn.functional as F
from torch_geometric.nn import GraphConv, GATConv, GCNConv
from torch_geometric.nn import global_mean_pool


class GNN(torch.nn.Module):

    def __init__(self, num_node_features, hidden_channels):
        super().__init__()
        self.conv1 = GATConv(num_node_features, hidden_channels, edge_dim=1)
        self.conv2 = GATConv(hidden_channels, hidden_channels, edge_dim=1)
        self.conv3 = GATConv(hidden_channels, hidden_channels, edge_dim=1)
        self.linear = Linear(hidden_channels, 1)


    def forward(self, x, edge_index, edge_weight, batch):
        x = self.conv1(x, edge_index, edge_attr=edge_weight)
        x = x.relu()
        x = self.conv2(x, edge_index, edge_attr=edge_weight)
        x = x.relu()
        x = self.conv3(x, edge_index, edge_attr=edge_weight)
        x = global_mean_pool(x, batch)
        x = F.dropout(x, p=0.6, training=self.training)
        x = self.linear(x)
        x = F.sigmoid(x)
        return x
