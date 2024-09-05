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

def parse_csv(path):
    victims = []
    with open(path, 'r') as csv:
        for line in csv:
            victim = {}
            line_vec = line.split(',')
            victim['seq'] = int(line_vec[0])
            victim['position'] = (0, 0)
            data = {}
            data['qPA'] = float(line_vec[3])
            data['pulse'] = float(line_vec[4])
            data['respiratory_freq'] = float(line_vec[5])
            victim['data'] = data
            victims.append(victim)
    return victims

def generate_pred_txt(victims):
    filename = "blind_test/pred.txt"
    content = ""
    for victim in victims:
        content += f"{victim["seq"]}, {0}, {0}, {victim["severity"]}, {1}\n"
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(content)



def teste_cego():
    path = "./datasets/data_408v_94x94/env_vital_signals_cego.txt"
    victims = parse_csv(path)
    predict(victims)
    generate_pred_txt(victims)
            
#teste_cego()
