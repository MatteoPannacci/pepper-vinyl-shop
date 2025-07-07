from utils.emotion_recognition import train_and_save


train_and_save(
    train_dir = "./data/emotions/train",
    val_dir = "./data/emotions/test",
    model_path = "./models/classifier",
    epochs = 10
)