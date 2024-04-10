import random as rd
import matplotlib.pyplot as plt

def k_means(victims, clusters = 4, max_iter = 100):
    x_min, x_max, y_min, y_max = get_limits(victims) 
    #initiate centroids
    centroids = []
    for _ in range(clusters):
        cx = rd.randint((-1)*x_min, x_max-1)
        cy = rd.randint((-1)*y_min, y_max-1)

        centroids.append([cx, cy, []])
    
    changed = True
    it = 0

    while it < max_iter and changed:
        changed = False

        #Clears the victim list of each centroid
        for c in centroids:
            c[2].clear()

        #Finds the closest centroid to each victim
        for id, data in victims:
            min_dist = -1
            closest = -1
            coord = data[0]
            
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
                c[0] = rd.randint((-1)*int(x_min/2), int(x_max/2))
                c[1] = rd.randint((-1)*int(y_min/2), int(y_max/2))
            

        it += 1

    return centroids

def get_limits(victims):
    x_max, x_min, y_max, y_min = -1, -1, -1, -1 
    for _, data in victims:
        x = data[0][0]
        y = data[0][1]

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

ix = []
iy = []

for _ in range(30):
    ix.append(rd.randint(-100, 100))
    iy.append(rd.randint(-100, 100))

victims = []
for i in range(len(ix)):
    victims.append((ix[i], iy[i]))

centroids = k_means(victims, (100, 100))

cx = []
cy = []

for c in centroids:
    cx.append(c[0])
    cy.append(c[1])

plt.figure(figsize=(12,8))
ax = plt.gca()

ax.set_xlim((-100, 100))
ax.set_ylim((-100, 100))

plt.grid()
plt.plot(ix, iy, 'o')
plt.plot(cx, cy, 'x')
plt.show()
