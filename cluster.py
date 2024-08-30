import random as rd
import matplotlib.pyplot as plt
import json

def k_means(victims, clusters = 4, max_iter = 100):
    x_min, x_max, y_min, y_max = __get_limits(victims) 
    #initiate centroids
    print(f"{x_min}, {x_max}, {y_min}, {y_max}")
    centroids = []
    for _ in range(clusters):
        cx = rd.randint(x_min, x_max-1)
        cy = rd.randint(y_min, y_max-1)

        centroids.append([cx, cy, []])
    
    changed = True
    it = 0

    while it < max_iter and changed:
        changed = False

        #Clears the victim list of each centroid
        for c in centroids:
            c[2].clear()

        #Finds the closest centroid to each victim
        for victim in victims:
            min_dist = -1
            closest = -1
            coord = victim["position"]

            # find the closest centroid to that victim
            for i, c in enumerate(centroids):
                c_dist = (c[0] - coord[0])**2 +  (c[1] - coord[1])**2
                if c_dist < min_dist or min_dist == -1:
                    min_dist = c_dist
                    closest = i

            centroids[closest][2].append(victim)
        
        #Calculates the new position for each centroid
        for c in centroids:
            n = len(c[2])
            x, y = 0, 0
            old_x, old_y = c[0], c[1]
            for victim in c[2]:
                coord = victim["position"]
                x += coord[0]
                y += coord[1]
            
            if n != 0:
                c[0] = x/n
                c[1] = y/n
                if c[0] != old_x or c[1] != old_y:
                    changed = True
            else:
                c[0] = rd.randint(int(x_min/2), int(x_max/2))
                c[1] = rd.randint(int(y_min/2), int(y_max/2))
            

        it += 1

    return centroids

def __get_limits(victims):
    x_max, x_min, y_max, y_min = -1, -1, -1, -1
    for victim in victims:
        coord = victim["position"]
        x, y = coord
        if x_max == -1 or x_min == -1:
            x_max = x;
            x_min = x;
        if y_max == -1 or y_min == -1:
            y_max = y
            y_min = y
        
        if x > x_max:
            x_max = x
        elif x < x_min:
            x_min = x

        if y > y_max:
            y_max = y
        elif y < y_min:
            y_min = y

    return x_min, x_max, y_min, y_max


def save_clusters(clusters):
    for i, cluster in enumerate(clusters):
        file_name = f"data/cluster{i}_300v_90x90.json"
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(cluster[2], f, ensure_ascii=False, indent=4)


def save_clusters_txt(clusters):
    for i, cluster in enumerate(clusters):
        file_name = f"data/cluster{i}_408v_94x94.txt"
        cluster_string = ""
        for victim in cluster[2]:
            cluster_string += f"{victim["seq"]},{victim["position"][0]},{victim["position"][1]},{victim["severity"]},1\n"
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(cluster_string)

def save_map(map):
    str_map = {}
    for key, val in map.map_data.items():
        str_key = f"{key[0]},{key[1]}"
        str_map[str_key] = val

    file_name = f"data/map_300v_90x90.json"
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(str_map, f, ensure_ascii=False, indent=4)


def load_clusters():
    clusters = []
    for i in range(4):
        file_name = f"data/cluster{i}_300v_90x90.json"
        with open(file_name, 'r',encoding='utf-8') as file:
            cluster = json.load(file)
            for victim in cluster:
                pos_tuple = (victim["position"][0], victim["position"][1])
                victim["position"] = pos_tuple
            clusters.append(cluster)

    print(clusters)
    return clusters

def load_map():
    file_name = f"data/map_300v_90x90.json"
    str_map = {}
    with open(file_name, 'r',encoding='utf-8') as file:
        str_map = json.load(file)
    
    parsed_map = {}
    for str_key, val in str_map.items():
        coords = str_key.split(",")
        key = (int(coords[0]), int(coords[1]))
        parsed_map[key] = val 

    return parsed_map
