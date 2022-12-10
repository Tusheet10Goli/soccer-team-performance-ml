import os
import torch
from torch.nn import MSELoss
from torch.optim import Adam
from torch_geometric.loader import DataLoader
from data import load_local_data
from model import GNN
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

path = '../weights'
if not os.path.exists(path):
    os.makedirs(path)

dataset, metadata = load_local_data()
train_loader = DataLoader(dataset[:int(len(dataset) * 0.7)], batch_size=32, shuffle=True)
test_loader = DataLoader(dataset[int(len(dataset) * 0.7):],
                         shuffle=True, batch_size=len(dataset[int(len(dataset) * 0.7):]))

model = GNN(metadata['num_node_features'], 64)
optimizer = Adam(model.parameters(), lr=0.0001)
criterion = MSELoss()
total_losses = []

for epoch in range(5000):
    total_loss = 0
    for data in train_loader:
        optimizer.zero_grad()
        out = model(data.x, data.edge_index, data.edge_attr, data.batch)
        loss = criterion(out.reshape(-1), data.y)
        loss.backward()
        total_loss += loss.item()
        optimizer.step()
    total_losses.append(total_loss)
    print(f'Epoch: {epoch}, Total Loss: {total_loss}')

torch.save(model.state_dict(), f'{path}/saved_weights.pt')

model = GNN(metadata['num_node_features'], 64)
model.load_state_dict(torch.load(f'{path}/saved_weights.pt'))

data = next(iter(test_loader))
y_pred = model(data.x, data.edge_index, data.edge_attr, data.batch).detach().numpy()
error = mean_squared_error(data.y, y_pred)
print(f'Test MSE Error: {error}')

plt.plot(range(len(total_losses)), total_losses)
plt.title('Training Loss with GATConv')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.show()
