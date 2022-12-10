import torch
from torch.nn import MSELoss
from torch.optim import Adam
from torch_geometric.loader import DataLoader
from data import load_local_data
from cheb_conv_model import ChebGNN

dataset, metadata = load_local_data()
print(dataset)
print(metadata)
train_loader = DataLoader(dataset[:int(len(dataset) * 0.7)], batch_size=32, shuffle=True)
test_loader = DataLoader(dataset[int(len(dataset) * 0.7):],
                         shuffle=True, batch_size=len(dataset[int(len(dataset) * 0.7):]))

model = ChebGNN(metadata['num_node_features'], 64)
optimizer = Adam(model.parameters(), lr=1e-5)
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

torch.save(model.state_dict(), 'cheb_conv.pt')
