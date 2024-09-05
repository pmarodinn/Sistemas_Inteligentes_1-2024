import matplotlib.pyplot as plt 
from vs.constants import DATA 

def read_cluster(filepath):
    cluster = []
    victims = []
    with open(filepath, 'r') as file:
        for i, line in enumerate(file):
            if i == 0:
                for val in line.split(','):
                    cluster.append(float(val.strip()))

            else:
                data = line.split(',')
                x = int(data[1].strip())
                y = int(data[2].strip())
                victims.append((x, y))
    
    cluster.append(victims)
    return cluster


def calc_sse(cluster):
    sum = 0
    cx, cy = cluster[0], cluster[1]
    for x, y in cluster[2]:
        sum += (cx-x)**2 + (cy-y)**2

    return sum

for i in range(4):
    filepath = f"./data/cluster{i}_{DATA.SCENARIO}.txt"
    cluster = read_cluster(filepath)

    print(f"cluster{i} - x: {cluster[0]}, y: {cluster[1]}")
    for x, y in cluster[2]:
        print(f"Victim - x: {x}, y: {y}")

    print(f"SSE cluster{i}: {calc_sse(cluster)}")
