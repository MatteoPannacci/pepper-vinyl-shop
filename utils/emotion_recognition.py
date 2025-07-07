import os
import numpy as np
import pandas as pd
import tensorflow as tf
import pickle

from PIL import Image
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split


# Ensure TensorFlow 1.x compatibility
if tf.__version__.startswith('2'):
    tf.compat.v1.disable_eager_execution()


def load_dataset(data_dir):

    X = []
    y = []
    classes = sorted(os.listdir(data_dir))
    for label in classes:
        class_dir = os.path.join(data_dir, label)
        if not os.path.isdir(class_dir):
            continue
        for fname in os.listdir(class_dir):
            if fname.endswith(".png"):
                fpath = os.path.join(class_dir, fname)
                try:
                    img = Image.open(fpath).convert('L').resize((48, 48))
                    img_array = np.array(img).astype(np.float32) / 255.0
                    X.append(img_array)
                    y.append(label)
                except:
                    continue
    X = np.expand_dims(np.array(X), axis=-1)
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)
    return X, y, label_encoder


def build_model():

    model = tf.keras.models.Sequential([
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(48, 48, 1)),
        tf.keras.layers.MaxPooling2D(2, 2),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D(2, 2),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(3, activation='softmax')
    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    return model


def train_and_save(train_dir, val_dir, model_path, epochs):

    X_train, y_train, label_encoder = load_dataset(train_dir)
    X_val, y_val, _ = load_dataset(val_dir)

    model = build_model()
    model.fit(X_train, y_train, epochs=epochs, validation_data=(X_val, y_val), batch_size=32)

    model_json = model.to_json()
    with open(model_path + "_model.json", "w") as json_file:
        json_file.write(model_json)

    model.save_weights(model_path + "_weights.h5")

    with open(model_path + "_label_encoder.pkl", "wb") as f:
        pickle.dump(label_encoder, f)


def predict_emotion(image_path, model_path_prefix):

    with open(model_path_prefix + "_model.json", "r") as json_file:
        model_json = json_file.read()
    model = tf.keras.models.model_from_json(model_json)
    model.load_weights(model_path_prefix + "_weights.h5")

    with open(model_path_prefix + "_label_encoder.pkl", "rb") as f:
        label_encoder = pickle.load(f)

    img = Image.open(image_path).convert('L').resize((48, 48))
    img_array = np.array(img).astype(np.float32) / 255.0
    img_array = np.reshape(img_array, (1, 48, 48, 1))

    preds = model.predict(img_array)
    class_index = np.argmax(preds, axis=1)[0]
    return label_encoder.inverse_transform([class_index])[0]
