from utils.neural_recommendation import train_model

train_model(
    hidden_dim=64,
    epochs=2000,
    lr=0.001,
    num_samples=1024,
    top_k=5
)