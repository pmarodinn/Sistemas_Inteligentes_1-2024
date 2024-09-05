import random
import numpy as np

from pandas.core.reshape.merge import uuid
import matplotlib.pyplot as plt

from search import search

def eval_seq_light(
    sequence, victims
):

    score = 0.0
    for i in range(len(sequence) -1):
        vic_index = next((index for (index, v) in enumerate(victims) if v["seq"] == sequence[i]), None)
        next_index = next((index for (index, v) in enumerate(victims) if v["seq"] == sequence[i+1]), None)
        cur_victim = victims[vic_index]
        next_victim = victims[next_index]
        
        sq_distance = (cur_victim["position"][0] - next_victim["position"][0])**2 + (cur_victim["position"][1] - next_victim["position"][1])**2
        victim_severity = 100 -cur_victim["severity"]


        a = (len(sequence) - i)
        b = 100*((i+1)*2)
        score += (a*(victim_severity) - sq_distance/b)

    return score

def select_best(scores_dict):
    sorted_sequences = sorted(scores_dict, key=lambda x: x[0], reverse=True)
    sorted_sequences = list(map(lambda x: x[1], sorted_sequences))
    return sorted_sequences[: len(sorted_sequences) // 2]

def mutate(sequence, prob = 0.05):
    threshold = int(0.05 * 1000)
    for i in range(len(sequence)):
        k = random.randint(0, 1000)
        if k < threshold:
            j = random.randint(0, len(sequence)-1)
            aux = sequence[j]
            sequence[j] = sequence[i] 
            sequence[i] = aux

def mutate_pop(population):
    for seq in population:
        mutate(seq)

def crossover(sequence1, sequence2):
    cross_point = random.randint(0, len(sequence1))
    
    child = sequence1[: cross_point] + sequence2[cross_point:]
    child = [i for n, i in enumerate(child) if i not in child[n + 1 :]]
    control_set = set(child)
    
    for seq in sequence1:
        if seq not in control_set:
            child.append(seq)

    return child

def reproduce_pop(population):
    children = []
    for i in range(len(population) - 1):
        sequence1 = population[i]
        sequence2 = population[i + 1]
        child = crossover(sequence1, sequence2)
        children.append(child)
    children.append(crossover(population[0], population[len(population) - 1]))

    return children


def initialize_random(victims, n_sequences):
    sequences = []
    vic_list = []
    for victim in victims:
        vic_list.append(victim["seq"])
    for _ in range(n_sequences):
        sequence = vic_list[:]
        random.shuffle(sequence)
        sequences.append(sequence)
    return sequences


def apply_natural_selection(population, victims):
    scores = []
    for sequence in population:
        score = eval_seq_light(sequence, victims)
        scores.append((score, sequence))

    return max(scores, key=lambda x: x[0])


def seq_list2dict(seqs, victims):
    victim_list = []
    for seq in seqs:
        for victim in victims:
            if victim["seq"] == seq:
                victim_list.append(victim)
                break
    return victim_list


victims = [
    {"seq": 1},
    {"seq": 2},
    {"seq": 3},
    {"seq": 4},
    {"seq": 5},
    {"seq": 6},
    {"seq": 7},
    {"seq": 8},
    {"seq": 9},
    {"seq": 10},
]
scores_dict = {
    "a": 14.0,
    "b": 25.0,
    "c": 20.0,
    "d": 17.0,
    "e": 13.0,
    "f": 1.0,
    "g": 30.0,
    "h": 27.0,
}
