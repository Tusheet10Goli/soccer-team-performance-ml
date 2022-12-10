import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import time


windowSize = 5
outputs = pd.read_csv("outputs-{}-window".format(windowSize))
inputs = pd.read_csv("inputs-{}-window".format(windowSize))
b = outputs["Goal Difference"].values.flatten()
A = inputs.loc[:, ~inputs.columns.isin(["Date", "Home", "Away"])].values
print("number of samples: ", len(A))
assert len(A) == len(b)

# make custom Dataset for use in training loop
class MatchDataset(Dataset):
    def __init__(self, matches, labels):
        self.matches = matches
        # normalize data
        normalizationFactor = np.max(np.abs(matches),axis=0)
        matches /= normalizationFactor
        pd.DataFrame(normalizationFactor).to_csv("aman-model-norm-factors", index=False)
        self.labels = labels

    def __len__(self):
        return len(self.matches)

    def __getitem__(self, index):
        match = self.matches[index,:]
        label = self.labels[index]
        return (torch.FloatTensor(match), torch.FloatTensor([label]))

# make training and test datasets
X_train, X_test, y_train, y_test = train_test_split(A, b, test_size=0.1, random_state=10)
training_dataset = MatchDataset(X_train, y_train)
testing_dataset = MatchDataset(X_test, y_test)
training_dataloader = DataLoader(training_dataset, batch_size=32, shuffle=True)
testing_dataloader = DataLoader(testing_dataset, batch_size=32, shuffle=True)

# define model
class MatchModel(nn.Module):

    def __init__(self):
        super().__init__()
        self.first_linear = nn.Linear(41, 100)
        self.first_dropout = nn.Dropout(p=0.5)
        self.second_linear = nn.Linear(100, 50)
        self.second_dropout = nn.Dropout(p=0.3)
        self.third_linear = nn.Linear(50, 1)
        self.relu = nn.functional.relu

    def forward(self, x):
        x = self.first_linear(x)
        x = self.first_dropout(x)
        x = self.relu(x)
        x = self.second_linear(x)
        x = self.second_dropout(x)
        x = self.relu(x)
        x = self.third_linear(x)
        return x

# initialize model, loss func, optimizer
model = MatchModel()
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters())

# training on a CPU (yuck!)
def train_model(model, criterion, optim, iterator, dubbo=False):
    model.train()
    total_loss = 0
    for x, y in iterator:
        optim.zero_grad()
        y_hat = model(x)
        loss = criterion(y_hat, y)
        total_loss += loss
        loss.backward()
        optim.step()
    return total_loss

def evaluate(model, iterator):
    pred, real = [], []
    model.eval()
    with torch.no_grad():
        for x, y in iterator:
            y_hat = model(x)
            for ground_truth, prediction in zip(y, y_hat):
                pred.append(prediction.item())
                real.append(ground_truth.item())
    return sum([(y - y_hat) ** 2 for y, y_hat in zip(pred, real)]) / len(pred)

start = time.time()
for epoch in range(15):
    loss = train_model(model, criterion, optimizer, training_dataloader)
    accuracy = evaluate(model, training_dataloader)
    print(f'Training epoch {epoch}, Goal MSE: {accuracy}')
end = time.time()

print(f'Testing Dataset, Goal MSE: {evaluate(model, testing_dataloader)}')
print("training time: ", end - start)

torch.save(model.state_dict(), "aman-model")