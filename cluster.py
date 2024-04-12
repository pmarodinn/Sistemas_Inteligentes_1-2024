import random as rd
import matplotlib.pyplot as plt

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
        for id, data in victims.items():
            min_dist = -1
            closest = -1
            coord, _ = data

            # find the closest centroid to that victim
            for i, c in enumerate(centroids):
                c_dist = (c[0] - coord[0])**2 +  (c[1] - coord[1])**2
                if c_dist < min_dist or min_dist == -1:
                    min_dist = c_dist
                    closest = i

            centroids[closest][2].append((id, coord))

        
        #Calculates the new position for each centroid
        for c in centroids:
            n = len(c[2])
            x, y = 0, 0
            old_x, old_y = c[0], c[1]
            for v in c[2]:
                x += v[1][0]
                y += v[1][1]
            
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
    print(victims)
    for _id , data in victims.items():
        coord, _ = data
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
        file_name = f"data/cluster{i}_300v_90x90.txt"
        
        contents =f"{cluster[0]},{cluster[1]}\n" 

        for victim in cluster[2]:
            id = victim[0]
            x = victim[1][0]
            y = victim[1][1]
            contents += f"{id},{x},{y},0.0,1\n"

        with open(file_name, 'w') as file:
            file.write(contents)
