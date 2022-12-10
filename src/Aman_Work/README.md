# Aman's Model:

I use statistics (collected from fbref.com) to train a neural network to predict goal differences. The data scraping is 
all in the `data` folder, the training code is all in the `model` folder, and the api endpoint that completed the inference
is in the `api` folder. The way the inference works is:

1) you provide a list of 11 players
2) the 11 players' average statistics over their last 100 appearances is aggregated to get an overall team statistic
3) this team statistic is subtracted from the average team statistics (derived from the last 5 seasons of premier league play)
4) this team statistic difference is then passed onto the model for inference, which outputs an expected goal difference
5) this goal difference is passed through a sigmoid function and then normalized to a score between 0 and 100


