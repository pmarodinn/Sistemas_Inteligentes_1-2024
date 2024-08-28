import numpy as np
import seaborn as sns
import pandas as pd
from keras import models
from keras import layers
import keras
import matplotlib.pyplot as plt
import tensorflow as tf


def build_and_compile_model(norm):
    model = keras.Sequential(
        [
            norm,
            layers.Dense(64, activation="relu"),
            layers.Dense(64, activation="relu"),
            layers.Dense(1),
        ]
    )

    model.compile(loss="mean_absolute_error", optimizer=keras.optimizers.Adam(0.001))
    return model


def plot_loss(history):
    plt.plot(history.history["loss"], label="loss")
    plt.plot(history.history["val_loss"], label="val_loss")
    plt.ylim([0, 10])
    plt.xlabel("Epoch")
    plt.ylabel("Error]")
    plt.legend()
    plt.grid(True)


epochs = 700
batch_size = 32
column_names = [
    "seq",
    "pSist",
    "pDiast",
    "qPA",
    "pulse",
    "respiratory_freq",
    "severity",
    "severity_class",
]
data_file = "datasets/env_vital_signals.txt"
raw_dataset = pd.read_csv(
    data_file,
    names=column_names,
    na_values="?",
    comment="\t",
    sep=",",
    skipinitialspace=True,
)
dataset = raw_dataset.copy()
print(dataset.tail())


train_dataset = dataset.sample(frac=0.8, random_state=0)
test_dataset = dataset.drop(train_dataset.index)
sns.pairplot(
    train_dataset[["severity", "qPA", "pulse", "respiratory_freq"]], diag_kind="kde"
)

train_features = train_dataset.copy()
test_features = test_dataset.copy()
test_features.pop("seq")
test_features.pop("pSist")
test_features.pop("pDiast")
test_features.pop("severity_class")
train_features.pop("seq")
train_features.pop("pSist")
train_features.pop("pDiast")
train_features.pop("severity_class")

train_labels = train_features.pop("severity")
test_labels = test_features.pop("severity")

normalizer = layers.Normalization(axis=-1)
normalizer.adapt(np.array(train_features))

dnn_model = build_and_compile_model(normalizer)

history = dnn_model.fit(
    train_features, train_labels, validation_split=0.2, verbose=0, epochs=epochs
)
dnn_model.summary()
# plot_loss(history)
plt.show()

test_results = {}
test_results["dnn_model"] = dnn_model.evaluate(test_features, test_labels, verbose=0)
print(pd.DataFrame(test_results, index=["Mean absolute error"]).T)

test_predictions = dnn_model.predict(test_features).flatten()

a = plt.axes(aspect="equal")
plt.scatter(test_labels, test_predictions)
plt.xlabel("True Values [MPG]")
plt.ylabel("Predictions [MPG]")
lims = [0, 50]
plt.xlim(lims)
plt.ylim(lims)
_ = plt.plot(lims, lims)

plt.show()

error = test_predictions - test_labels
plt.hist(error, bins=25)
plt.xlabel("Prediction Error [MPG]")
_ = plt.ylabel("Count")

plt.show()

dnn_model.save("best.keras")
