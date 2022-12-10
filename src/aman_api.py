import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import math
from pathlib import Path
import time

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

model = MatchModel()
model.load_state_dict(torch.load("aman-model"))
model.eval()
normalizationFactor = pd.read_csv("aman-model-norm-factors").values.flatten()

averagePlayers = pd.read_csv("average-players")
allPlayers = pd.read_csv("all-players")
averageTeam = pd.read_csv("average-team")

def getAllPlayers():
    return allPlayers

def inference(inputDF):
    players = inputDF["Player"].values
    for player in players:
        assert player in allPlayers["Player"].values

    playersDF = averagePlayers.loc[averagePlayers["Player"].isin(players)]
    # assert len(playersDF) == 11, "You need to select 11 valid players"
    team = dict()
    averageMinutes = playersDF["Minutes"].sum()
    for stat in averageTeam.columns:
        assert len(averageTeam[stat]) == 1
        team[stat] = playersDF[stat].sum()  - (averageTeam[stat].iloc[0] * averageMinutes/990.0)
    teamDF = pd.DataFrame([team])
    
    inferenceInputNP = teamDF.values.astype(normalizationFactor.dtype).flatten()
    inferenceInput = torch.Tensor(inferenceInputNP / normalizationFactor)

    # method of least squares - MSE of ~ 2.8
    # x = pd.read_csv("least-squares").values
    # goalDifference = np.dot(inferenceInput, x).flatten()[0]

    # neural network model - MSE of ~ 2.2
    goalDifference = model(inferenceInput).item() # TODO: figure this out
    sigmoidGD = 1/(1 + math.e ** (-5 * (goalDifference - 0.15))) # this gives reasonable response
    return sigmoidGD * 100


## Test Code
arsenal = [
    "Alexandre Lacazette",
    "Danny Welbeck", 
    "Mesut Özil", 
    "Granit Xhaka", 
    "Mohamed Elneny", 
    "Alex Oxlade-Chamberlain",
    "Héctor Bellerín",
    "Sead Kolašinac",
    "Nacho Monreal",
    "Rob Holding",
    "Petr Čech"
]

mancity = [
    "Bernardo Silva",
    "Raheem Sterling",
    "Riyad Mahrez",
    "İlkay Gündoğan",
    "Fernandinho",	
    "Kevin De Bruyne",
    "Oleksandr Zinchenko",
    "Aymeric Laporte",
    "Rúben Dias",
    "João Cancelo",
    "Ederson"
]

norwich = [
    "Tim Krul",
    "Max Aarons",
    "Ben Gibson",
    "Grant Hanley",
    "Ozan Kabak",
    "Mathias Normann",
    "Pierre Lees-Melou",
    "Teemu Pukki",
    "Kenny McLean",
    "Josh Sargent",
    "Dimitris Giannoulis"
]

## Easy Cases
arsenalDF = pd.DataFrame([{"Player": p} for p in arsenal])
mancityDF = pd.DataFrame([{"Player": p} for p in mancity])
norwichDF = pd.DataFrame([{"Player": p} for p in norwich])

print("Arsenal Score: ", inference(arsenalDF))
print("Man City Score: ", inference(mancityDF))
print("Norwich Score: ", inference(norwichDF))


## Medium Cases
mancity.remove("Kevin De Bruyne")
mancity.remove("Raheem Sterling")
mancity.append("Héctor Bellerín")
mancity.append("Andrew Robertson")
mancityDF = pd.DataFrame([{"Player": p} for p in mancity])
print("Man City (more defenders) Score: ", inference(mancityDF))
# reset
mancity.append("Raheem Sterling")
mancity.append("Kevin De Bruyne")
mancity.remove("Héctor Bellerín")
mancity.remove("Andrew Robertson")
# remove goalie 
mancity.remove("Ederson")
mancity.append("Héctor Bellerín")
mancityDF = pd.DataFrame([{"Player": p} for p in mancity])
start = time.time()
result = inference(mancityDF)
end = time.time()
print("Man City (no goalie) Score: ", result)
print("time taken: ", end - start)

# Hard Cases - 

attackers = [
    "Raheem Sterling",
    "Riyad Mahrez",
    "Jamie Vardy",	
    "Kevin De Bruyne",
    "Granit Xhaka",
    "Alexandre Lacazette",
    "Raheem Sterling",
    "Riyad Mahrez",
    "Jamie Vardy",	
    "Kevin De Bruyne",
    "Granit Xhaka",
]
attackerDF = pd.DataFrame([{"Player": p} for p in attackers])
print("All Attackers Score: ", inference(attackerDF))




    



