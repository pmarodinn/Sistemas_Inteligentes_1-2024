import numpy as np
import keras

def predict(victims: list[dict]):
    try:
        model = keras.saving.load_model("best.keras")
    except:
        print("model not found, generate it with generate_model.py")
        exit(1)
    victim_data = []
    for victim in victims:
        data = victim["data"]
        row = [ data["qPA"], data["pulse"], data["respiratory_freq"], ]
        victim_data.append(row)
    victim_data = np.array(victim_data)
    predictions = model.predict(victim_data)
    for victim, severity_pred in zip(victims, predictions.flatten()):
        victim["severity"] = float(severity_pred)
