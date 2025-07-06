from utils.neural_recommendation import train_model

train_model(
    hidden_dim=32,
    epochs=500,
    lr=0.01,
    num_samples=1024
)