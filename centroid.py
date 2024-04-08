import random as rd

def k_means(individuals, size ,clusters = 4, max_iter = 20):
    
    #initiate centroids
    centroids = []
    for _i in range(clusters):
        cx = rd.randint(0, size[0]-1)
        cy = rd.randint(0, size[1]-1)

        centroids.append((cx, cy, []))
    
    changed = True
    it = 0

    while it < max_iter and changed:
        changed = False

        #Clears the individual list of each centroid
        for c in centroids:
            c[2].clear()

        #Finds the closest centroid to each individual
        for ind in individuals:
            min_dist = -1
            closest = -1
            
            # find the closest centroid to that individual
            for i, c in enumerate(centroids):
                c_dist = (c[0] - ind[0])**2 +  (c[1] - ind[1])**2
                if c_dist < min_dist or min_dist == -1:
                    min_dist = c_dist
                    closest = i

            centroids[closest][2].append(ind)

        
        #Calculates the new position for each centroid
        for c in centroids:
            n = len(c[2])
            x, y = 0, 0
            old_x, old_y = c[0], c[1]
            for ind in c[2]:
                x += ind[0]
                y += ind[1]
            
            c[0] = x/n
            c[1] = y/n

            if c[0] != old_x or c[1] != old_y:
                changed = True
            

        it += 1

    return centroids


